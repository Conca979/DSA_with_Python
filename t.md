# BiLSTM + Luong Attention Seq2Seq — Complete Verified Trace

> Reference files cross-checked: `notation_convention (1).md` and `dimension_trace.md`.
> **2 confirmed bugs found** — documented in §0 below. All shapes in this document are the corrected source of truth.

---

## §0 — Bugs Found in Reference Files

| # | File | Where | Error | Correct Value |
|---|---|---|---|---|
| **B1** | `notation_convention.md` | §7, `W_c` shape | Written as `(d, 2d)` — implies column-vector convention `W·x`, but the whole project uses row-vector `x @ W` | Should be `(2d, d)` = `(1024, 512)` |
| **B2** | `dimension_trace.md` | End checklist, line `h_t^enc[l].shape` | Written as `(B, d)` — but the *combined* (both-direction) output `h_t^enc[l]` is the concatenation `[fwd;bwd]`, shape `(B, 2d)` | Should be `(B, 2d) = (64, 1024)` for combined; individual directions are each `(B, d)` |

> [!WARNING]
> **B1** is the most dangerous bug — it will silently produce the wrong weight matrix size if you copy the shape directly from `notation_convention.md`. Use `(2d, d)` everywhere in code.

---

## §1 — Hyperparameter Table (Concrete Values Used Throughout)

| Symbol | Meaning | Value |
|---|---|---|
| `B` | batch size | **64** |
| `e` | embedding dim | **256** |
| `d` | LSTM hidden dim | **512** |
| `V` | shared vocab | **16 000** |
| `L` | stacked LSTM layers | **2** |
| `D` | num directions (encoder only) | **2** (decoder = 1) |
| `Tx` | encoder padded length, this batch | **20** |
| `Ty` | decoder padded length, this batch | **18** |
| `4d` | gate pre-activation width | **2 048** |
| `2d` | bidirectional concat width | **1 024** |

**Convention everywhere:** row-vector batch-first. All linear layers are `y = x @ W + b`.

---

## §2 — Complete Weight Catalogue

### 2.1 Embeddings

| Symbol | Shape | Size |
|---|---|---|
| `Ex` | `(V, e)` = `(16000, 256)` | encoder embedding table |
| `Ey` | `(V, e)` = `(16000, 256)` | decoder embedding table |

### 2.2 Encoder LSTM Weights — per layer `l`, per direction `dir ∈ {fwd, bwd}`

| Layer | Weight | Shape | Params |
|---|---|---|---|
| `l=1` | `W_ih^enc,dir[1]` | `(e, 4d)` = `(256, 2048)` | 524 288 |
| `l=1` | `W_hh^enc,dir[1]` | `(d, 4d)` = `(512, 2048)` | 1 048 576 |
| `l=1` | `b^enc,dir[1]` | `(4d,)` = `(2048,)` | 2 048 |
| `l=2` | `W_ih^enc,dir[2]` | **(2d, 4d) = (1024, 2048)** ← because layer-2 input = `[fwd;bwd]` concat from layer 1 | 2 097 152 |
| `l=2` | `W_hh^enc,dir[2]` | `(d, 4d)` = `(512, 2048)` | 1 048 576 |
| `l=2` | `b^enc,dir[2]` | `(4d,)` = `(2048,)` | 2 048 |

× 2 directions → **8 separate weight matrices + 4 biases** for the encoder.

### 2.3 Bridge Projection Weights

| Symbol | Shape | Purpose |
|---|---|---|
| `W_bridge_H` | `(2d, d)` = `(1024, 512)` | project top-layer `H_raw` sequence → `H` for attention |
| `b_bridge_H` | `(d,)` = `(512,)` | |
| `W_bridge_h[l]` (×2 layers) | `(2d, d)` = `(1024, 512)` | project final encoder `h` → decoder init `h_0^dec[l]` |
| `b_bridge_h[l]` (×2) | `(d,)` = `(512,)` | |
| `W_bridge_C[l]` (×2 layers) | `(2d, d)` = `(1024, 512)` | project final encoder `C` → decoder init `C_0^dec[l]` |
| `b_bridge_C[l]` (×2) | `(d,)` = `(512,)` | |

### 2.4 Decoder LSTM Weights — per layer `l` (unidirectional, D=1)

| Layer | Weight | Shape |
|---|---|---|
| `l=1` | `W_ih^dec[1]` | `(e, 4d)` = `(256, 2048)` |
| `l=1` | `W_hh^dec[1]` | `(d, 4d)` = `(512, 2048)` |
| `l=1` | `b^dec[1]` | `(4d,)` = `(2048,)` |
| `l=2` | `W_ih^dec[2]` | `(d, 4d)` = `(512, 2048)` ← decoder layer-2 input is `d`-wide (single direction) |
| `l=2` | `W_hh^dec[2]` | `(d, 4d)` = `(512, 2048)` |
| `l=2` | `b^dec[2]` | `(4d,)` = `(2048,)` |

### 2.5 Attention + Output Weights

| Symbol | Shape | Note |
|---|---|---|
| `W_a` | `(d, d)` = `(512, 512)` | Luong "general" score projection |
| `W_c` | **(2d, d) = (1024, 512)** ← corrected from notation_convention.md | fusion weight |
| `b_c` | `(d,)` = `(512,)` | fusion bias |
| `Wy` | `(d, V)` = `(512, 16000)` | output projection |
| `by` | `(V,)` = `(16000,)` | output bias |

---

## §3 — LSTM Cell Formula (used everywhere — encoder fwd/bwd/decoder all identical math)

Given: input `x_t: (B, in_dim)`, previous hidden `h_prev: (B, d)`, previous cell `C_prev: (B, d)`.

```
gates = x_t @ W_ih + h_prev @ W_hh + b          # (B, 4d)

i_t = σ( gates[:, 0*d : 1*d] )                  # input gate     (B, d)
f_t = σ( gates[:, 1*d : 2*d] )                  # forget gate    (B, d)
g_t = tanh( gates[:, 2*d : 3*d] )               # cell gate      (B, d)
o_t = σ( gates[:, 3*d : 4*d] )                  # output gate    (B, d)

C_t = f_t * C_prev + i_t * g_t                  # new cell state (B, d)
h_t = o_t * tanh(C_t)                           # new hidden     (B, d)
```

Where `σ = sigmoid`. All multiplications `*` are element-wise.

### Shape trace for a single LSTM step

| Tensor | Shape | Value |
|---|---|---|
| `x_t` | `(B, in_dim)` | varies by stage |
| `W_ih` | `(in_dim, 4d)` | varies by stage |
| `h_prev` | `(B, d)` | `(64, 512)` |
| `W_hh` | `(d, 4d)` | `(512, 2048)` |
| `b` | `(4d,)` | `(2048,)` |
| `gates` | `(B, 4d)` | `(64, 2048)` |
| `i_t, f_t, g_t, o_t` | each `(B, d)` | `(64, 512)` |
| `C_t` | `(B, d)` | `(64, 512)` |
| `h_t` | `(B, d)` | `(64, 512)` |

---

## §4 — Stage-by-Stage Forward Pass Shape Trace

### STAGE 0 — Raw Batch Input

| Symbol | Shape | Example |
|---|---|---|
| `X` | `(B, Tx)` | `(64, 20)` — encoder token ids |
| `Xlen` | `(B,)` | `(64,)` — true sentence lengths |
| `Yin` | `(B, Ty)` | `(64, 18)` — decoder input (`[START, v1, ...]`) |
| `Yout` | `(B, Ty)` | `(64, 18)` — decoder target (`[v1, ..., END]`) |
| `Ylen` | `(B,)` | `(64,)` — true target lengths |

---

### STAGE 1 — Embedding Lookup

```python
x_t = Ex[X[:, t]]          # for t in range(Tx)
y_t = Ey[Yin[:, t]]        # for t in range(Ty)
```

| Tensor | Shape |
|---|---|
| `Ex` | `(16000, 256)` |
| `X[:, t]` | `(64,)` — one column, integer ids |
| `x_t` | **(64, 256)** — one embedding per example |
| `Ey` | `(16000, 256)` |
| `y_t` | **(64, 256)** |

---

### STAGE 2 — Encoder BiLSTM, Layer 1

#### Loop structure
```
for t in range(Tx):           # fwd pass: t = 0 → 19
    x_t = Ex[X[:, t]]        # (64, 256)
    gates_fwd = x_t @ W_ih^enc,fwd[1] + h_prev_fwd @ W_hh^enc,fwd[1] + b^enc,fwd[1]
    ... (LSTM cell) ...
    store h_t_fwd[t], C_t_fwd[t]

for t in reversed(range(Tx)):  # bwd pass: t = 19 → 0
    x_t = Ex[X[:, t]]          # SAME embeddings, different traversal order
    gates_bwd = x_t @ W_ih^enc,bwd[1] + h_prev_bwd @ W_hh^enc,bwd[1] + b^enc,bwd[1]
    ... (LSTM cell) ...
    store h_t_bwd[t], C_t_bwd[t]
```

#### Per-step shape trace, Layer 1, `fwd`:

| Tensor | Shape | Computation |
|---|---|---|
| `x_t` | `(64, 256)` | input |
| `W_ih^enc,fwd[1]` | `(256, 2048)` | weight |
| `h_prev_fwd` | `(64, 512)` | init = zeros |
| `W_hh^enc,fwd[1]` | `(512, 2048)` | weight |
| `b^enc,fwd[1]` | `(2048,)` | bias |
| `gates` | `(64, 2048)` | `= x_t @ (256,2048) + h_prev @ (512,2048) + (2048,)` |
| `i,f,g,o` | each `(64, 512)` | split `gates` into 4 blocks |
| `C_t_fwd` | `(64, 512)` | `f*C_prev + i*g` |
| `h_t_fwd` | `(64, 512)` | `o * tanh(C_t)` |

Identical shape for `bwd`, different weights `W_ih^enc,bwd[1]`, `W_hh^enc,bwd[1]`.

#### Concatenate directions → feed Layer 2:

```python
h_t_enc1 = np.concatenate([h_t_fwd, h_t_bwd], axis=-1)   # (64, 1024)
```

| Tensor | Shape |
|---|---|
| `h_t_fwd` | `(64, 512)` |
| `h_t_bwd` | `(64, 512)` |
| `h_t^enc[1]` = `[fwd ; bwd]` | **(64, 1024)** |

---

### STAGE 2b — Encoder BiLSTM, Layer 2

Now input per step is `h_t^enc[1]: (64, 1024)` — note the wider `W_ih`.

#### Per-step shape trace, Layer 2, `fwd`:

| Tensor | Shape | Note |
|---|---|---|
| `h_t^enc[1]` | `(64, 1024)` | input to this layer |
| `W_ih^enc,fwd[2]` | **(1024, 2048)** | wider input weight |
| `h_prev_fwd[2]` | `(64, 512)` | init = zeros |
| `W_hh^enc,fwd[2]` | `(512, 2048)` | same as layer 1 |
| `gates` | `(64, 2048)` | `= (64,1024)@(1024,2048) + (64,512)@(512,2048) + (2048,)` |
| `i,f,g,o` | each `(64, 512)` | split |
| `C_t_fwd[2]` | `(64, 512)` | |
| `h_t_fwd[2]` | `(64, 512)` | |

Same for `bwd`. Concatenate:

```python
h_t^enc[2] = [h_t_fwd[2] ; h_t_bwd[2]]   # (64, 1024)
```

#### Collect all timesteps → H_raw:

```python
H_raw = np.stack([h_t^enc[2] for t in range(Tx)], axis=1)   # (64, 20, 1024)
```

| Tensor | Shape |
|---|---|
| each `h_t^enc[2]` | `(64, 1024)` |
| `H_raw` | **(64, 20, 1024)** |

---

### STAGE 3 — Bridge Projection

#### 3a — H_raw → H (sequence for attention)

```python
H = np.tanh(H_raw @ W_bridge_H + b_bridge_H)
#   (64,20,1024) @ (1024,512) + (512,) → (64,20,512)
```

| Tensor | Shape |
|---|---|
| `H_raw` | `(64, 20, 1024)` |
| `W_bridge_H` | `(1024, 512)` |
| `b_bridge_H` | `(512,)` |
| **`H`** | **(64, 20, 512)** ← this is what attention sees |

#### 3b — Final encoder states → decoder initial states (per layer `l`)

```python
# Gather true final states (example: layer l=1)
h_final_fwd[l] = h_fwd_states[l][np.arange(B), Xlen-1, :]   # (64, 512)
h_final_bwd[l] = h_bwd_states[l][:, 0, :]                    # (64, 512) — bwd always ends at t=0
h_final_enc[l] = np.concatenate([h_final_fwd[l], h_final_bwd[l]], axis=-1)  # (64, 1024)

h_0_dec[l] = np.tanh(h_final_enc[l] @ W_bridge_h[l] + b_bridge_h[l])   # (64, 512)
C_0_dec[l] = np.tanh(C_final_enc[l] @ W_bridge_C[l] + b_bridge_C[l])   # (64, 512)
```

| Tensor | Shape |
|---|---|
| `h_final_fwd[l]` | `(64, 512)` |
| `h_final_bwd[l]` | `(64, 512)` |
| `h_final_enc[l]` | `(64, 1024)` |
| `W_bridge_h[l]` | `(1024, 512)` |
| **`h_0_dec[l]`** | **(64, 512)** |
| **`C_0_dec[l]`** | **(64, 512)** |

Done for `l=1` and `l=2` separately (and `h` vs `C`): **4 bridge matmuls** total.

---

### STAGE 4 — Decoder LSTM (Unidirectional, L=2)

```python
for t in range(Ty):
    y_t = Ey[Yin[:, t]]    # (64, 256)
    # --- Layer 1 ---
    gates_dec1 = y_t @ W_ih^dec[1] + h_prev_dec1 @ W_hh^dec[1] + b^dec[1]
    # --- Layer 2 ---
    gates_dec2 = h_t_dec1 @ W_ih^dec[2] + h_prev_dec2 @ W_hh^dec[2] + b^dec[2]
    s_t = h_t_dec2          # top-layer hidden = attentional query
    # --- Attention ---
    # --- Fusion + Output ---
```

#### Layer 1 shape trace:

| Tensor | Shape | Computation |
|---|---|---|
| `y_t` | `(64, 256)` | decoder embedding input |
| `W_ih^dec[1]` | `(256, 2048)` | |
| `h_prev_dec1` | `(64, 512)` | init = `h_0_dec[1]` from bridge |
| `W_hh^dec[1]` | `(512, 2048)` | |
| `gates_dec1` | `(64, 2048)` | |
| `h_t_dec1` | `(64, 512)` | LSTM cell output |

#### Layer 2 shape trace:

| Tensor | Shape | Computation |
|---|---|---|
| `h_t_dec1` | `(64, 512)` | input from layer 1 |
| `W_ih^dec[2]` | `(512, 2048)` | ← (d,4d) not (2d,4d) — decoder is unidirectional! |
| `h_prev_dec2` | `(64, 512)` | init = `h_0_dec[2]` |
| `W_hh^dec[2]` | `(512, 2048)` | |
| `gates_dec2` | `(64, 2048)` | |
| **`s_t`** = `h_t_dec2` | **(64, 512)** | attentional query |

---

### STAGE 5 — Luong "General" Attention

```python
temp  = s_t @ W_a                                          # (64,512) @ (512,512) = (64,512)
e_t   = np.einsum('bd,btd->bt', temp, H)                  # (64,20)
M     = (np.arange(Tx) < Xlen[:, None]).astype(float)     # (64,20) — padding mask
e_t   = e_t + (M - 1) * 1e9                               # mask: pad positions → -∞
alpha_t = softmax(e_t, axis=1)                            # (64,20)  rows sum to 1
z_t   = np.einsum('bt,btd->bd', alpha_t, H)              # (64,512) — context vector
```

| Tensor | Shape | Meaning |
|---|---|---|
| `s_t` | `(64, 512)` | decoder query |
| `W_a` | `(512, 512)` | score projection |
| `temp` | `(64, 512)` | projected query |
| `H` | `(64, 20, 512)` | encoder memory |
| `e_t` | `(64, 20)` | raw attention scores |
| `M` | `(64, 20)` | mask (1=real, 0=pad) |
| `alpha_t` (= `α_t`) | **(64, 20)** | attention weights |
| `z_t` | **(64, 512)** | context vector |

---

### STAGE 6 — Fusion

```python
concat  = np.concatenate([z_t, s_t], axis=-1)      # (64, 1024)
s_tilde = np.tanh(concat @ W_c + b_c)              # (64, 512)
#                 (64,1024) @ (1024,512) + (512,)
```

| Tensor | Shape |
|---|---|
| `z_t` | `(64, 512)` |
| `s_t` | `(64, 512)` |
| `concat` | `(64, 1024)` |
| `W_c` | **(1024, 512)** ← corrected shape |
| `b_c` | `(512,)` |
| **`s̃_t`** | **(64, 512)** |

---

### STAGE 7 — Output Projection

```python
logits_t = s_tilde @ Wy + by      # (64,512) @ (512,16000) + (16000,) = (64, 16000)
p_t      = softmax(logits_t, axis=1)   # (64, 16000)
y_hat_t  = np.argmax(p_t, axis=1)     # (64,) — inference only
```

| Tensor | Shape |
|---|---|
| `s̃_t` | `(64, 512)` |
| `Wy` | `(512, 16000)` |
| `by` | `(16000,)` |
| `logits_t` | **(64, 16000)** |
| `p_t` | `(64, 16000)` |
| `ŷ_t` | `(64,)` |

---

### STAGE 8 — Loss

```python
logits = np.stack(all_logits_t, axis=1)            # (64, 18, 16000)
mask   = (Yout != PAD).astype(float)               # (64, 18)
loss   = masked_cross_entropy(logits, Yout, mask)  # scalar
```

| Tensor | Shape |
|---|---|
| `logits` | `(64, 18, 16000)` |
| `mask` | `(64, 18)` |
| `L` | **scalar** |

---

## §5 — Full Numeric Worked Example (One Full Forward Pass, t=0)

**Setup (tiny toy batch, B=2 for readability, all other dims kept real):**

```
B=2, e=4, d=4, V=8, Tx=3, Ty=2, L=1 (simplified to 1 layer for this example)
4d = 16
```

### Step 0 — Input

```
X     = [[5, 2, 0],   # example 0: tokens 5,2 + PAD
         [3, 7, 1]]   # example 1: tokens 3,7,1 (full length)
Xlen  = [2, 3]
Yin   = [[START=2, 6],
         [START=2, 4]]
```

### Step 1 — Embedding lookup (t=0)

```
Ex = random (8, 4) matrix, e.g.:
Ex[5] = [0.1, 0.2, -0.1, 0.3]    # example 0's token at t=0
Ex[3] = [0.5, -0.1, 0.2, 0.4]    # example 1's token at t=0

x_0 = Ex[X[:, 0]] = Ex[[5, 3]]
    = [[0.1,  0.2, -0.1,  0.3],
       [0.5, -0.1,  0.2,  0.4]]     shape: (2, 4)
```

### Step 2 — Encoder fwd LSTM, Layer 1, t=0

```
h_prev = zeros(2, 4)
C_prev = zeros(2, 4)

W_ih = (4, 16)   ← random init (not shown for space)
W_hh = (4, 16)

gates = x_0 @ W_ih + h_prev @ W_hh + b
     ← (2,4)@(4,16) + (2,4)@(4,16) + (16,)
     = (2, 16)          ← 2 examples × 16 values

Split into 4 blocks of width d=4:
  i_0  = σ(gates[:, 0:4])     (2,4)
  f_0  = σ(gates[:, 4:8])     (2,4)
  g_0  = tanh(gates[:, 8:12]) (2,4)
  o_0  = σ(gates[:, 12:16])   (2,4)

C_0 = f_0 * C_prev + i_0 * g_0    (2,4)   ← C_prev=0 → C_0 = i_0 * g_0
h_0_fwd = o_0 * tanh(C_0)         (2,4)
```

### Step 3 — Encoder bwd LSTM, Layer 1, t=Tx-1=2 (reversed loop starts here)

```
x_2 = Ex[X[:, 2]] = Ex[[0, 1]]    # PAD for ex0, token 1 for ex1
                                   # (2, 4)
(bwd hidden runs: h_init_bwd = zeros)
gates_bwd = x_2 @ W_ih_bwd + zeros @ W_hh_bwd + b_bwd
h_2_bwd = ... (2, 4)
```

After full encoder loop for the 1-layer simplified case:

```
H_raw: shape (2, 3, 8)   ← each t: concat [h_t_fwd (2,4), h_t_bwd (2,4)]
```

> In real 2-layer case: H_raw is `(B, Tx, 2d)` = `(64, 20, 1024)`.

### Step 4 — Bridge H_raw → H

```
H = tanh(H_raw @ W_bridge_H + b_bridge_H)
  = tanh((2,3,8) @ (8,4) + (4,))
  = (2, 3, 4)                   ← (B, Tx, d)
```

### Step 5 — Bridge final states → decoder init

```
h_final_fwd = h_fwd_states[Xlen-1]  →  index [1] for ex0, [2] for ex1
            = (2, 4)
h_final_bwd = h_bwd_states[:, 0, :]  # bwd's t=0 state (always)
            = (2, 4)
h_final_enc = concat([h_final_fwd, h_final_bwd], axis=-1) = (2, 8)

h_0_dec = tanh((2,8) @ (8,4) + (4,)) = (2, 4)
C_0_dec = tanh((2,8) @ (8,4) + (4,)) = (2, 4)
```

### Step 6 — Decoder step t=0

```
y_0 = Ey[Yin[:, 0]] = Ey[[2, 2]] = [[..], [..]]  (2, 4)  ← START token embedding

# Decoder LSTM (1 layer simplified):
gates_dec = y_0 @ W_ih_dec + h_0_dec @ W_hh_dec + b_dec
          = (2,4)@(4,16) + (2,4)@(4,16) + (16,)
          = (2, 16)

s_0 = h_0_dec_new     (2, 4)
```

### Step 7 — Attention at t=0

```
temp    = s_0 @ W_a          (2,4)@(4,4) = (2,4)
e_0     = einsum('bd,btd->bt', temp, H)
        = (2, 3)              ← scores over 3 encoder positions

Mask:
M = [[1, 1, 0],    # ex0: Xlen=2, positions 0,1 are real
     [1, 1, 1]]    # ex1: Xlen=3, all real
                   (2, 3)

e_0_masked = e_0 + (M-1)*1e9   # ex0's position 2 → -∞
           = (2, 3)

alpha_0 = softmax(e_0_masked, axis=1)    (2, 3)   ← ex0: alpha[:,2] ≈ 0
                                                     ex1: all 3 positions contribute

z_0 = einsum('bt,btd->bd', alpha_0, H)  (2, 4)    ← weighted encoder memory
```

### Step 8 — Fusion + Output at t=0

```
concat  = [z_0 ; s_0]   = (2, 8)
s_tilde = tanh((2,8) @ (8,4) + (4,)) = (2, 4)

logits_0 = s_tilde @ Wy + by    (2,4)@(4,8) + (8,) = (2, 8)
p_0      = softmax(logits_0, axis=1)   (2, 8)    ← probability over 8 vocab tokens
y_hat_0  = argmax(p_0, axis=1)         (2,)
```

### Step 9 — Loss (after collecting both decoder steps t=0,1)

```
logits = stack([logits_0, logits_1], axis=1)    (2, 2, 8)
Yout   = [[6, END], [4, END]]
mask   = [[1, 1], [1, 1]]   (all real, no padding in this tiny example)
L      = mean(cross_entropy(logits[b,t,:], Yout[b,t]) * mask[b,t])   → scalar
```

---

## §6 — Corrected End-to-End Shape Checklist

```python
# Paste these assertions into your code as sanity checks
assert X.shape      == (B, Tx)
assert Yin.shape    == (B, Ty)
assert x_t.shape    == (B, e)              # (64, 256) — every encoder t

# Encoder single-direction per step:
assert h_t_fwd.shape == (B, d)            # (64, 512)
assert h_t_bwd.shape == (B, d)            # (64, 512)

# Combined (per t, layer l) — NOTE: (B, 2d) not (B, d)
assert h_t_enc_combined.shape == (B, 2*d) # (64, 1024) ← bug B2 was here

# After stacking all t:
assert H_raw.shape  == (B, Tx, 2*d)       # (64, 20, 1024)

# After bridge:
assert H.shape      == (B, Tx, d)         # (64, 20, 512)

# Decoder init (per layer):
assert h_0_dec.shape == (B, d)            # (64, 512)
assert C_0_dec.shape == (B, d)            # (64, 512)

# Decoder hidden at each step (top layer = query):
assert s_t.shape    == (B, d)             # (64, 512)

# Attention:
assert alpha_t.shape == (B, Tx)           # (64, 20) — rows sum to 1
assert z_t.shape     == (B, d)            # (64, 512)

# Fusion:
assert s_tilde_t.shape == (B, d)          # (64, 512)

# Output:
assert logits_t.shape == (B, V)           # (64, 16000)

# Collected:
assert logits.shape   == (B, Ty, V)       # (64, 18, 16000)
```

---

## §7 — Open Questions for You

Before moving to the backward pass and NumPy/CuPy code:

1. **Teacher forcing vs scheduled sampling?** — Decoder input at step `t+1`: always `Yin[:,t]` (teacher forcing), or sometimes use `ŷ_t` from the previous step?
2. **Padding in bwd encoder pass** — Do you want to zero out PAD positions *before* feeding them into the bwd LSTM, or only mask the loss? The notation file recommends starting bwd at `Xlen[b]-1`, but that requires per-example indexing (slower). Preference?
3. **Shared embeddings `Ex = Ey`?** — The notation file says "shared vocab ≠ shared weights". Do you want to tie them anyway (saves `V×e` = 4M params)?
4. **Numerical precision** — Float32 (CuPy default) or Float64? Mixed precision?
5. **Gradient checkpointing** — With `Tx=20`, `L=2`, `D=2`, you store `80` LSTM states during forward. That's fine for CuPy. If Tx grows large, gradient checkpointing (recompute states during backward) becomes relevant.
6. **Next step** — Ready for the backward pass (BPTT) formulas + shapes, or first the CuPy code skeleton?
