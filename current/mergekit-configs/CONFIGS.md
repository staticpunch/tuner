# Designs

Who every do this is geninus.
Here's a markdown table showing common merge methods and their key parameters:

| Method | Description | Key Parameters | Base Model Required |
|--------|-------------|----------------|---------------------|
| Linear | Simple weighted average | `weight`, `normalize` | No |
| TIES | Task vector merging with sparsification | `weight`, `density`, `normalize` | Yes |
| SLERP | Spherical interpolation | `t` | Yes |
| Task Arithmetic | Merging task vectors linearly | `weight`, `lambda`, `normalize` | Yes |
| DARE | Random pruning with rescaling | `weight`, `density`, `normalize` | Yes |
| Model Breadcrumbs | Discards small and large deltas | `weight`, `density`, `gamma` | Yes |
| Model Stock | Geometric weight computation | `filter_wise` | Yes |
| DELLA | Adaptive magnitude-based pruning | `weight`, `density`, `epsilon` | Yes |
| SCE | Variance-based matrix merging | `weight`, `density`, `select_topk` | Yes |


Here's a markdown table summarizing the merging strategies for the checkpoints:

| Strategy | First Step | Second Step | Method 1 | Method 2 | Base Model | Note |
|----------|------------|-------------|----------|----------|------------|------|
| exp_00a only | Direct Linear merge | None | Linear | None | None | Simple baseline approach |
| exp_01a only | Direct TIES merge | None | TIES | None | INSTRUCT | Task vector approach |
| exp_00a → exp_00b | Linear merge CKPT_1,2,3 | Linear with INSTRUCT | Linear | Linear | None | Equal weights (normalized) for all models |
| exp_00a → exp_00c | Linear merge CKPT_1,2,3 | SLERP with INSTRUCT | Linear | SLERP | INSTRUCT | Uses attention/MLP gradients in SLERP |
| exp_01a → exp_01b | TIES merge CKPT_1,2,3 | TIES with INSTRUCT | TIES | TIES | INSTRUCT → BASE | Two-level base model approach |
| exp_01a → exp_01c | TIES merge CKPT_1,2,3 | SLERP with INSTRUCT | TIES | SLERP | INSTRUCT | Combines TIES and SLERP benefits |
