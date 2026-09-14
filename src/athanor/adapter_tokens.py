"""Strict completion-only token masking primitives; no model loading or training."""


def completion_tokens(tokenizer, prompt, completion, *, max_length):
    """Use the installed pinned template; reject non-prefix or truncated examples.

    Template compatibility must be proved with the real local processor. The
    synthetic tests exercise invariants, not Qwen tokenizer compatibility.
    """
    if type(max_length) is not int or max_length < 2:
        raise ValueError("Explicit max_length >= 2 required")
    if (not isinstance(prompt, list) or any(not isinstance(m, dict) for m in prompt)
            or [m.get("role") for m in prompt] != ["system", "user"]):
        raise ValueError("Expected system/user prompt")
    if not isinstance(completion, list) or len(completion) != 1:
        raise ValueError("Expected one assistant completion")
    if not isinstance(completion[0], dict) or completion[0].get("role") != "assistant":
        raise ValueError("Completion must be assistant")
    for message in prompt + completion:
        if set(message) != {"role", "content"} or not isinstance(message["content"], str):
            raise ValueError("Only text messages are supported")
        if not message["content"].strip():
            raise ValueError("Empty message")
    prefix = tokenizer.apply_chat_template(prompt, tokenize=True, add_generation_prompt=True,
                                           enable_thinking=False)
    full = tokenizer.apply_chat_template(prompt + completion, tokenize=True,
                                         add_generation_prompt=False, enable_thinking=False)
    for ids in (prefix, full):
        if not isinstance(ids, list) or not ids or any(type(i) is not int or i < 0 for i in ids):
            raise ValueError("Template must return a flat nonempty token ID list")
    if len(full) <= len(prefix) or full[:len(prefix)] != prefix:
        raise ValueError("Template does not preserve the prompt prefix or has no completion")
    if len(full) > max_length:
        raise ValueError("Example exceeds max_length; silent truncation is forbidden")
    return {"input_ids": full, "attention_mask": [1] * len(full),
            "labels": [-100] * len(prefix) + full[len(prefix):]}


def pad_examples(examples, *, pad_token_id):
    if not examples or type(pad_token_id) is not int or pad_token_id < 0:
        raise ValueError("Nonempty examples and explicit pad token ID required")
    width = max(len(row["input_ids"]) for row in examples)
    batch = {key: [] for key in ("input_ids", "attention_mask", "labels")}
    for row in examples:
        size = len(row["input_ids"])
        if not size or len(row["labels"]) != size or len(row["attention_mask"]) != size:
            raise ValueError("Token/mask/label lengths differ")
        if all(label == -100 for label in row["labels"]):
            raise ValueError("No supervised completion tokens")
        for key, padding in (("input_ids", pad_token_id), ("attention_mask", 0), ("labels", -100)):
            batch[key].append(row[key] + [padding] * (width - size))
    return batch
