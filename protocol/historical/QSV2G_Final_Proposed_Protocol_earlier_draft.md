Yes. Now we can turn the ideas into **one complete proposed protocol** and explain it from beginning to end using one concrete Tesla → Tata Power scenario.

I will keep the original QSKA components where they are useful, make **QSS the central new authorization mechanism**, and add the other improvements only where they solve a specific protocol problem.

> **Important:** the Tesla/Tata Power/Jalandhar values below are a **demonstration scenario**, not a claim that Tata Power or Tesla currently deploys this protocol. The original QSKA paper is the source for the QSKA baseline; the QSS + context-binding + enhanced response architecture is **our proposed extension**. QSKA_A_Quantum_Secured_Privacy-…

# 1. Our final protocol in one picture

```text
                         ┌──────────────────────┐
                         │       EV             │
                         │  Tesla Model 3       │
                         │  PID = PID-73A91     │
                         └──────────┬───────────┘
                                    │
                           ① Authentication
                           PID + Proof + Nonce
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │ Tata Power CS        │
                         │ CS-JAL-01            │
                         └──────────┬───────────┘
                                    │
                          ② Authorization Request
                                    │
                  ┌─────────────────┼─────────────────┐
                  │                 │                 │
                  ▼                 ▼                 ▼
             ┌─────────┐       ┌─────────┐       ┌─────────┐
             │ UC-A    │       │ UC-B    │       │ UC-C    │
             │ Home RA │       │ Utility │       │ Grid    │
             └────┬────┘       └────┬────┘       └────┬────┘
                  │                 │                 │
                  │ Share A         │ Share B         │ Share C
                  └─────────────────┼─────────────────┘
                                    │
                         ③ Verifiable 2-of-3 QSS
                                    │
                                    ▼
                         Authorization = ACCEPT
                                    │
                                    ▼
                              Tata Power CS
                                    │
                     ④ Authenticated response
                         + session binding
                                    │
                                    ▼
                              Tesla EV
                                    │
                         ⑤ Verify response
                                    │
                                    ▼
                             START CHARGING
```

The research story is therefore:

\[
\boxed{\text{QSKA}\rightarrow\text{Privacy-Preserving Authentication}}
\]

\[
\boxed{\text{QSS}\rightarrow\text{Distributed Threshold Authorization}}
\]

\[
\boxed{\text{Context Binding + Fresh Session}
\rightarrow\text{Anti-Replay / Anti-Substitution}}
\]

\[
\boxed{\text{Authenticated Response}
\rightarrow\text{Integrity + Authenticity + Confidentiality}}
\]

---

# 2. The characters and demo data

Let's establish fixed values so that we can follow the same vehicle throughout the entire protocol.

### EV

```text
Vehicle:
Tesla Model 3

Real identity:
EV-TESLA-JAL-001

Pseudo-identity:
PID-73A91

Password/credential:
PwdEV = EV@9281

EV nonce:
NE = 839274
```

The **real identity is not sent to the charging station**.

The EV uses:

\[
PID_{EV}=PID\text{-}73A91
\]

This continues the privacy-preserving idea from QSKA.

---

### Charging station

```text
Charging Station:
TATA-CS-JAL-01

Location:
Jalandhar Highway

Station nonce:
NC = 482615
```

---

### Three authorities

For our proposed system:

```text
UC-A = Home / Registration Authority
UC-B = Visited Utility Authority
UC-C = Independent Grid / Trust Authority
```

These are **logical roles in our proposed architecture**, not three entities specified by the original QSKA paper.

---

# 3. Step 0 — Registration

Before Tesla ever arrives at the charging station, registration occurs.

The original QSKA already has registration involving EV, CS and UC, including secret material and pseudo-identity generation. QSKA_A_Quantum_Secured_Privacy-…

Our extension changes the trust architecture.

Instead of:

```text
                 UC
                /  \
               EV  CS
```

we have:

```text
                UC-A
                 │
          ┌──────┼──────┐
          │      │      │
        UC-A    UC-B   UC-C
          │      │      │
          └──────┼──────┘
                 │
              QSS shares
```

Suppose the authorization secret is conceptually:

\[
S_{auth}=A7F2C91B
\]

We don't give this complete secret to any one authority.

Using a **2-of-3 threshold QSS** scheme:

```text
UC-A → ShareA
UC-B → ShareB
UC-C → ShareC
```

The important property is:

\[
Share_A + Share_B
\Rightarrow Authorization
\]

or:

\[
Share_A + Share_C
\Rightarrow Authorization
\]

or:

\[
Share_B + Share_C
\Rightarrow Authorization
\]

but:

\[
Share_A
\not\Rightarrow Authorization
\]

So a single compromised authority cannot independently authorize charging.

---

# 4. Step 1 — Tesla reaches the Tata charging station

Tesla arrives.

It wants:

```text
Operation = CHARGE
```

Tesla generates:

\[
N_E=839274
\]

and a timestamp:

\[
TS_E=18:42:10
\]

It creates its privacy-preserving request.

Conceptually:

\[
Req_{EV}=
PID_{EV}
\parallel
Proof_{EV}
\parallel
N_E
\parallel
TS_E
\parallel
Operation
\]

Demo:

```text
PID       = PID-73A91
Proof     = HMAC(...)
Nonce     = 839274
Timestamp = 18:42:10
Operation = CHARGE
```

Then:

```text
Tesla EV
    │
    │ Authentication Request
    ▼
Tata Power CS-JAL-01
```

---

# 5. Step 2 — CS verifies the EV

The charging station first checks the authentication information.

This is where the original QSKA idea is retained:

```text
EV
 ↓
Pseudo-identity
 ↓
Authentication proof
 ↓
UC/backend verification
 ↓
EV authenticated
```

So we are **not replacing QSKA authentication with QSS**.

This distinction is very important:

> **QSKA answers: "Is this a legitimate EV?"**

> **QSS answers: "Do enough independent authorities authorize this operation?"**

---

# 6. Step 3 — Create the authorization context

This is one of our important improvements.

We don't simply ask:

```text
"Can PID-73A91 charge?"
```

Instead, we create a unique authorization context.

\[
AC=
H(
PID_{EV}
\parallel
ID_{CS}
\parallel
SID
\parallel
Operation
\parallel
N_E
\parallel
TS
)
\]

First we need a session identifier.

Suppose:

\[
SID=SID\text{-}928174
\]

Then:

```text
PID       = PID-73A91
CS        = TATA-CS-JAL-01
SID       = SID-928174
Operation = CHARGE
Nonce     = 839274
Timestamp = 18:42:10
```

These are bound together.

Conceptually:

\[
AC=H(
PID\text{-}73A91
\parallel
TATA\text{-}CS\text{-}JAL\text{-}01
\parallel
SID\text{-}928174
\parallel
CHARGE
\parallel
839274
\parallel
18{:}42{:}10)
\]

Suppose:

\[
AC=9F71A2...
\]

That value represents **this exact charging authorization request**.

---

# 7. Why this context binding is important

Suppose an attacker captures an old authorization:

```text
PID-73A91
CS-JAL-01
ACCEPT
```

and tries to use it at:

```text
CS-DEL-05
```

The authorization context changes:

\[
AC_{JAL}\neq AC_{DEL}
\]

Therefore the old authorization cannot simply be reused.

Similarly:

```text
CHARGE
```

cannot automatically be transformed into:

```text
DISCHARGE
```

because:

\[
AC_{CHARGE}\neq AC_{DISCHARGE}
\]

This is a major improvement in authorization design.

---

# 8. Step 4 — CS asks the three authorities

CS sends the authorization context to the three authorities.

```text
                   Authorization Context
                          AC = 9F71A2...
                               │
          ┌────────────────────┼────────────────────┐
          ▼                    ▼                    ▼
       UC-A                 UC-B                 UC-C
```

Each authority checks its own policy.

### UC-A

```text
PID valid?              YES
Session valid?          YES
Operation permitted?    YES
```

Therefore:

```text
UC-A = APPROVE
```

### UC-B

```text
PID valid?              YES
Session valid?          YES
Operation permitted?    YES
```

Therefore:

```text
UC-B = APPROVE
```

### UC-C

Suppose it is temporarily unavailable:

```text
UC-C = NO RESPONSE
```

---

# 9. Step 5 — 2-of-3 QSS authorization

Now:

```text
UC-A → valid share
UC-B → valid share
UC-C → unavailable
```

Threshold:

\[
t=2
\]

Available valid shares:

\[
2
\]

Therefore:

\[
2\geq2
\]

and:

\[
Authorization=ACCEPT
\]

This is the core new mechanism.

---

# 10. But we improve QSS with share verification

We don't blindly trust:

```text
Share A
Share B
```

Each share should be verifiable.

Conceptually:

\[
Verify(Share_i,AC)=1
\]

Only if:

\[
Verify(Share_i,AC)=1
\]

does the share participate.

This handles the case where a malicious UC sends a fake/corrupted share.

So:

```text
UC-A → Share A → VALID ✓
UC-B → Share B → VALID ✓
UC-C → no response
```

Result:

```text
2 valid shares
       ↓
Threshold satisfied
       ↓
ACCEPT
```

---

# 11. We should NOT expose the long-term secret

This is another important design decision.

We don't want:

```text
Share A
Share B
      ↓
Reconstruct master secret
      ↓
CS receives master secret
```

Instead:

```text
Share A
Share B
   ↓
Threshold authorization
   ↓
Authorization proof/token
   ↓
CS
```

So the long-term authorization secret stays protected.

The CS only receives what it needs to authorize **this particular session**.

---

# 12. Step 6 — Generate authorization token

Suppose the threshold process produces:

\[
AuthToken=
H(
AC
\parallel
"AUTHORIZED"
\parallel
Validity
)
\]

Demo:

```text
Authorization = ACCEPT
PID            = PID-73A91
CS             = TATA-CS-JAL-01
SID            = SID-928174
Operation      = CHARGE
EnergyLimit    = 30 kWh
ValidUntil     = 19:42
```

Conceptually:

```text
AUTH-TOKEN =
AUTH-8A72F9...
```

Now the CS knows:

> The required number of independent authorities approved **this particular EV, this particular station, this particular session and this particular operation**.

---

# 13. Step 7 — CS creates the charging response

Now we reach the part you were asking about earlier.

The CS does **not** send the QSS shares back to Tesla.

Instead:

```text
CS → EV
```

with an authenticated response.

For example:

\[
Response=
SID
\parallel
PID
\parallel
Decision
\parallel
Nonce
\parallel
TS
\parallel
AuthToken
\]

Demo:

```text
SID        = SID-928174
PID        = PID-73A91
Decision   = ACCEPT
Nonce      = 839274
Timestamp  = 18:42:12
AuthToken  = AUTH-8A72F9...
```

---

# 14. How do we protect this response?

This is where we use our **authenticated session protection**.

We have a session key:

\[
K_{EV-CS}
\]

For example, for demonstration:

```text
K_EV-CS = A91F73C2...
```

This is only a **toy value**; real implementation uses a cryptographically generated key.

We can use an authenticated-encryption primitive such as **Ascon-AEAD128**, which NIST standardized in SP 800-232 for lightweight authenticated encryption. 

Conceptually:

\[
(C,Tag)=
AEAD_{K_{EV-CS}}
(
Nonce,
Response,
AD
)
\]

So:

```text
CS
 │
 │ encrypted + authenticated response
 ▼
EV
```

The EV decrypts and verifies the authentication tag.

---

# 15. Step 8 — Tesla verifies the response

Tesla receives:

```text
C
Tag
Nonce
```

Tesla uses its session key:

\[
K_{EV-CS}
\]

and checks:

\[
Verify(Tag)=1
\]

If valid:

```text
✓ Correct CS
✓ Correct session
✓ Correct nonce
✓ Correct authorization response
✓ Message not modified
```

Then:

```text
Decision = ACCEPT
```

Tesla starts charging.

---

# 16. Complete scenario

Now put everything together:

```text
TESLA MODEL 3
PID = PID-73A91
        │
        │ 1. Authentication Request
        │    PID + Proof + Nonce
        ▼
TATA POWER CS
CS = TATA-CS-JAL-01
        │
        │ 2. Verify EV
        │
        │ 3. Create Authorization Context
        │
        │ AC = H(PID || CS || SID || Operation
        │        || Nonce || Timestamp)
        │
        ├──────────────► UC-A
        │                ✓ Approve
        │                ✓ Share A
        │
        ├──────────────► UC-B
        │                ✓ Approve
        │                ✓ Share B
        │
        └──────────────► UC-C
                         unavailable

                  2 valid shares
                         │
                         ▼
                  QSS THRESHOLD
                       2-of-3
                         │
                         ▼
                      ACCEPT
                         │
                         ▼
                    AUTH TOKEN
                         │
                         ▼
                    TATA CS
                         │
                         │ 4. Authenticated
                         │    encrypted response
                         ▼
                  TESLA MODEL 3
                         │
                         │ 5. Verify
                         ▼
                   START CHARGING
```

---

# 17. Now let's test the protocol against the attacks

This is where your research becomes interesting.

---

## Attack 1 — Session-key attack

Suppose an attacker wants to obtain:

\[
K_{EV-CS}
\]

The attacker observes:

```text
EV → CS
CS → EV
```

but does not possess the legitimate session secrets.

Our design uses a **fresh session**:

\[
SID=SID\text{-}928174
\]

and fresh nonces:

\[
N_E=839274
\]

\[
N_C=482615
\]

The session key is derived/bound to these values.

Conceptually:

\[
K_{EV-CS}
=
KDF(
K_{base},
PID,
SID,
N_E,
N_C
)
\]

Therefore a new charging session gets a different key.

Example:

```text
Monday:
K1 = 8A91...

Tuesday:
K2 = 72FD...
```

\[
K_1\neq K_2
\]

So compromising an old session key should not automatically expose future sessions, assuming the underlying key-establishment mechanism has the required forward-secrecy properties.

**Important:** we should not claim full forward secrecy merely from changing nonces. If we want to claim forward secrecy, we need a key-establishment mechanism that formally provides it.

---

# 18. Attack 2 — Man-in-the-middle

Attacker:

```text
             ATTACKER
            /        \
          EV          CS
```

Attacker tries:

```text
EV → Attacker → CS
```

But our protocol has several bindings.

The attacker cannot simply change:

```text
PID
CS
SID
Nonce
Operation
```

because they are incorporated into the authenticated context:

\[
AC=H(PID||CS||SID||Operation||Nonce||TS)
\]

and the final response is authenticated under:

\[
K_{EV-CS}
\]

If attacker changes:

```text
CHARGE
```

to:

```text
DISCHARGE
```

then:

\[
AC_{CHARGE}\neq AC_{DISCHARGE}
\]

The authorization is invalid.

---

# 19. Attack 3 — Impersonation

Suppose attacker says:

> "I am Tesla Model 3."

They send:

```text
PID-73A91
```

But possession of the pseudo-ID alone is insufficient.

The attacker also needs the legitimate authentication proof/session credentials.

So:

```text
PID only
     ↓
NOT ENOUGH
```

The attacker must pass the authentication stage.

Even if they somehow obtain the PID, they still face the distributed authorization stage.

And:

```text
1 UC
```

cannot authorize by itself.

This gives you **two layers**:

```text
Layer 1:
EV authentication

Layer 2:
Distributed authorization
```

---

# 20. Attack 4 — Replay attack

Suppose attacker recorded yesterday:

```text
ACCEPT
SID-111
Nonce-555
AUTH-TOKEN-XYZ
```

Today attacker sends exactly the same thing.

The EV/CS checks:

\[
SID
\]

and:

\[
Nonce
\]

and:

\[
Timestamp
\]

and the authorization context.

The old authorization was bound to:

```text
SID-111
Nonce-555
old timestamp
```

Today's session is:

```text
SID-928174
Nonce-839274
new timestamp
```

Therefore:

\[
AC_{old}\neq AC_{new}
\]

The replayed response is rejected.

---

# 21. Attack 5 — Message modification

Suppose legitimate response is:

```text
ACCEPT
```

Attacker changes it:

```text
REJECT
```

or:

```text
ACCEPT
→
DISCHARGE
```

The authentication tag was generated over the complete message/context.

For example:

\[
Tag=
MAC_K(
SID||PID||Decision||Nonce||TS
)
\]

After modification:

\[
Tag_{received}
\neq
Tag_{calculated}
\]

Therefore:

```text
✗ MESSAGE MODIFIED
✗ RESPONSE REJECTED
```

If AEAD is used, the same verification failure occurs.

---

# 22. Attack 6 — Eavesdropping

Suppose attacker sits on the communication channel:

```text
EV ─────────────── CS
       👁 attacker
```

They capture the response.

If the response is protected using authenticated encryption:

```text
Ciphertext = 91AF73C...
Tag        = 72BC...
```

The attacker cannot directly read:

```text
ACCEPT
SID
authorization information
```

without the session key.

Therefore:

\[
Plaintext \rightarrow Ciphertext
\]

and:

\[
K_{EV-CS}
\]

is required for decryption.

This provides confidentiality.

---

# 23. Attack 7 — Compromised utility center

This is arguably the **most important new attack** compared with centralized QSKA.

Suppose:

```text
Attacker compromises UC-A
```

Attacker obtains:

```text
Share A
```

Can attacker authorize Tesla?

No.

Because:

\[
Threshold=2
\]

and:

\[
1<2
\]

Therefore:

```text
UC-A compromised
       ↓
Only 1 share
       ↓
NO AUTHORIZATION
```

But:

```text
UC-A compromised
+
UC-B honest
+
UC-C honest
```

can still allow legitimate charging if the threshold is satisfied.

This is exactly why distributed authorization is useful.

---

# 24. What if a malicious UC sends a fake share?

Suppose:

```text
UC-A → valid
UC-B → FAKE
UC-C → valid
```

Our proposed verifiable-share mechanism checks:

```text
Share A → ✓
Share B → ✗
Share C → ✓
```

Therefore:

\[
2\ valid\ shares
\]

remain.

The authorization succeeds.

This is why **verifiable QSS** is a worthwhile addition rather than simply saying "we use QSS."

---

# 25. What if two authorities collude?

Now the security boundary must be stated honestly.

With 2-of-3:

\[
t=2
\]

If **two authorities collude**, they may potentially satisfy the threshold.

Therefore our claim should NOT be:

> "The system is secure even if any number of authorities are compromised."

Instead:

> **The protocol tolerates up to \(t-1\) compromised authorities for authorization security, under the security assumptions of the chosen QSS construction.**

For 2-of-3:

\[
t-1=1
\]

So the system is designed to tolerate **one compromised authority** without that authority being able to independently authorize an operation.

This limitation should actually appear in your threat model.

---

# 26. The final security mapping

This is the part I would put directly into your research architecture.

| Security requirement | Our mechanism | What it protects |
|---|---|---|
| EV authentication | QSKA authentication | Fake EV |
| EV privacy | Pseudo-ID | Real identity |
| Distributed trust | 2-of-3 QSS | Single-authority compromise |
| Share integrity | Verifiable QSS | Fake/malformed shares |
| Authorization binding | Context hash | Wrong EV/CS/session/operation |
| Session security | Fresh SID + nonces | Session reuse |
| Confidentiality | AEAD/session encryption | Eavesdropping |
| Integrity | Authentication tag | Message modification |
| Authenticity | Session authentication | Fake CS/EV response |
| Replay resistance | Nonce + timestamp + SID | Old messages |
| Authorization | Threshold decision | Unauthorized charging |
| Fine-grained control | Operation + limits + validity | Misuse of authorization |

---

# 27. And this is the key difference from original QSKA

Think about the two systems like this.

### Original QSKA

```text
EV
 │
 │ authenticate
 ▼
CS
 │
 ▼
Trusted UC
 │
 └── authorization/trust decision
```

The major trust assumption is:

> **UC is trusted.**

QSKA also uses pseudo-identities, HMAC, encryption/decryption, session keys, quantum communication/superdense coding and formal verification. QSKA_A_Quantum_Secured_Privacy-…

### Our proposed extension

```text
EV
 │
 │ QSKA authentication
 ▼
CS
 │
 │ authorization context
 ▼
┌─────────────┬─────────────┬─────────────┐
│    UC-A     │    UC-B     │    UC-C     │
│   Share A   │   Share B   │   Share C   │
└─────────────┴─────────────┴─────────────┘
              │
        2-of-3 QSS
              │
              ▼
       Authorization
              │
              ▼
             CS
              │
        Authenticated
          response
              │
              ▼
             EV
```

So the **new research problem** becomes:

> **What happens when the central trusted UC in QSKA cannot be fully trusted or is compromised?**

And our answer is:

> **Move the critical charging authorization decision from one trusted authority to a threshold-controlled distributed authorization layer using QSS, while strengthening the message/session design with context binding, freshness, verifiable shares, and authenticated encrypted responses.**

That is much more defensible as a research contribution than simply saying *"QSKA + QSS."*

---

## One final correction I would make to our protocol

I would **not yet finalize "Ascon" as a mandatory component**.

For the paper, we can define the requirement as:

\[
\boxed{\text{Authenticated Encryption}}
\]

and then experimentally compare:

```text
HMAC + Encryption
          vs
AEAD / Ascon-AEAD128
```

That gives you an **experimental research question** instead of an arbitrary algorithm choice.

The stronger core contribution remains:

\[
\boxed{
\text{QSKA}
+
\text{Verifiable Threshold QSS}
+
\text{Authorization Context Binding}
+
\text{Fresh Session}
+
\text{Authenticated Response}
}
\]

And the attack evaluation should explicitly test **session-key compromise, MITM, impersonation, replay, message modification, eavesdropping, malicious/fake QSS shares, and compromised-authority scenarios**.

**Confidence: 0.95.** The QSKA baseline is grounded in the uploaded paper; the threshold-QSS architecture, context binding, and strengthened response are our proposed extension. The exact security guarantees will ultimately depend on the specific QSS construction, key-establishment method, and formal security model we choose.
---

# FINAL INTEGRATION CHECK — REQUIRED FOR THE QSV2G PROTOCOL

This section consolidates the protocol elements that must be treated as part of the final QSV2G design when Astra converts this brief into the paper. It is an integration/correction section, not a replacement architecture.

## A. Complete CS-to-EV Response Design

The CS **must not send the individual QSS shares to the EV**. QSS shares remain at the authorization layer. After threshold authorization, the CS sends only the context-bound authorization result/proof to the EV through the authenticated session.

The response must bind the authorization to the current session and request. The preferred conceptual plaintext response is:

```text
Resp_plain = SID || PID || OP || Decision || N_E || N_C || TS_CS || LIM || VLD || AuthToken
```

The response is then protected using the selected session-protection mechanism:

```text
Option 1:
C   = Enc(K_EV-CS, Resp_plain)
Tag = HMAC(K_EV-CS, C || SID || N_E || N_C)

Option 2:
(C, Tag) = AEAD_K_EV-CS(Nonce_CS, Resp_plain, AD)
```

Ascon-AEAD128 remains an **optional implementation choice**, not a mandatory architectural requirement.

The EV accepts the response only after checking:

1. `SID` matches the active session.
2. `PID` matches the current pseudo-identity.
3. `N_E`/`N_C` correspond to the current request/session.
4. `TS_CS` is fresh and `VLD` has not expired.
5. `OP` is exactly the requested operation.
6. `LIM` is exactly the authorized energy/power limit.
7. `AuthToken` is valid and bound to the same authorization context.
8. HMAC/AEAD verification succeeds.
9. `Decision = ACCEPT`.

Only after all checks succeed may the EV proceed with the authorized CHARGE or DISCHARGE operation.

## B. Fine-Grained Authorization Is Part of the Protocol

The authorization context must bind not only `PID`, `CSID`, `SID`, operation, nonce and timestamp, but also the requested limit and validity:

\[
AC = H(PID || CSID || SID || OP || N_E || N_C || TS_E || TS_{CS} || LIM || VLD).
\]

Therefore a token/authorization issued for:

```text
CHARGE, 30 kWh, until 19:42
```

cannot automatically be reused for:

```text
DISCHARGE
```

or for a different limit, station, session, or validity interval.

## C. Both CHARGE and DISCHARGE Are Supported

`OP` is explicitly one of:

```text
CHARGE
DISCHARGE
```

The same threshold authorization architecture is used for both operations. The policy checks performed by UC-A, UC-B and UC-C may differ depending on the operation.

## D. Explicit 2-of-3 Availability Rule

The authorization decision is based on **valid verified shares**, not simply the number of responding authorities:

\[
Decision=ACCEPT \iff N_{valid\ shares}\ge 2.
\]

Examples:

| UC-A | UC-B | UC-C | Result |
|---|---|---|---|
| Valid | Valid | Valid | ACCEPT |
| Valid | Valid | Unavailable | ACCEPT |
| Valid | Unavailable | Valid | ACCEPT |
| Unavailable | Valid | Valid | ACCEPT |
| Valid | Invalid | Unavailable | REJECT |
| Invalid | Valid | Unavailable | REJECT |
| Valid | Unavailable | Unavailable | REJECT |
| Unavailable | Unavailable | Unavailable | REJECT |

Thus one unavailable authority does not prevent service, while two unavailable/invalid authorities prevent threshold authorization.

## E. Verifiable QSS Share Requirement

Every authority share must be checked before it contributes to threshold authorization:

\[
Verify(Share_i, AC)=1.
\]

A forged, corrupted, stale, or context-mismatched share is rejected and does not count toward the threshold.

The exact QSS/share-verification construction remains **to be specified** when the concrete verifiable QSS scheme is selected. Do not invent the missing construction in the final paper.

## F. Long-Term Authorization Secret Must Not Be Exposed Unnecessarily

The preferred architecture is:

```text
UC shares
   ↓
verify context-bound shares
   ↓
2-of-3 threshold authorization
   ↓
short-lived AuthToken / authorization proof
   ↓
CS
```

The EV and CS should not receive or permanently store the complete long-term `S_auth` merely to complete one authorization. If a concrete QSS construction requires temporary reconstruction internally, that detail must be defined explicitly and the long-term secret must not be treated as a normal session credential.

## G. Controlled Identity Disclosure

Normal operation uses only `PID`.

A separate policy-controlled disclosure procedure may be invoked when accountability is legally/operationally required:

```text
Normal:
PID used for authentication/authorization

Exceptional authorized disclosure:
PID → controlled multi-authority procedure → ID_EV
```

This is an architectural extension, not a fully specified cryptographic subprotocol yet. The final paper must not claim a concrete threshold identity-disclosure algorithm unless one is actually selected and defined.

## H. Revocation

Each authority can perform revocation/policy checks before issuing its share:

\[
Revoked(PID)=1 \Rightarrow Share_i\;not\;issued.
\]

A revoked EV therefore cannot obtain the required two valid approvals.

Threshold-controlled revocation updates can be included as a future/extension procedure, but the normal authorization protocol already incorporates revocation status checking.

## I. Emergency / Recovery

Emergency recovery is separate from the normal charging/discharging path. The QSS-protected authorization material should have a controlled recovery process for severe infrastructure failures.

The exact emergency recovery protocol remains **out of the core protocol until a concrete mechanism is selected**. It must not be presented as already implemented.

## J. Security-Claim Boundary

The protocol uses fresh SIDs/nonces/timestamps for freshness and session binding. This must **not** be described as proof of forward secrecy.

Forward secrecy may be claimed only if the final key-establishment construction actually provides it and is formally analyzed. Otherwise the paper should state:

> QSV2G provides fresh per-session keying/binding but does not claim forward secrecy from nonce freshness alone.

Similarly, the paper must not claim that QSS automatically gives unconditional security to the entire QSV2G protocol. The security of the complete construction depends on the selected QSS, authentication, key-establishment and authenticated-encryption mechanisms.

## K. Exact Items Still To Be Instantiated

The following are intentionally not invented in this protocol brief:

1. Concrete verifiable QSS construction.
2. Exact share-generation equation.
3. Exact share-verification/commitment equation.
4. Exact threshold authorization-proof/token construction.
5. Exact KDF/key-establishment construction if different from QSKA.
6. Concrete threshold identity-disclosure mechanism.
7. Concrete threshold revocation-update mechanism, if implemented.
8. Concrete emergency-recovery mechanism, if implemented.
9. Final AEAD primitive, if Ascon-AEAD128 is selected experimentally.

These should be filled only after the corresponding concrete algorithms are selected and justified.

## L. Final End-to-End QSV2G Flow

```text
1. EV registration / pseudo-identity setup
2. CS registration
3. 2-of-3 QSS authorization-share setup among UC-A/UC-B/UC-C
4. EV sends QSKA-style privacy-preserving authentication request
5. EV and CS are authenticated
6. Fresh session SID/nonces/session key established
7. CS creates context:
   AC = H(PID || CSID || SID || OP || nonces || timestamps || LIM || VLD)
8. CS sends AC to UC-A, UC-B and UC-C
9. Each UC performs local policy/revocation checks
10. Each approving UC returns a verifiable context-bound share
11. CS verifies every share
12. If ≥2 valid shares exist, threshold authorization succeeds
13. Generate/obtain a short-lived context-bound AuthToken/proof
14. CS creates protected response containing:
    SID || PID || OP || Decision || nonces || timestamp || LIM || VLD || AuthToken
15. CS sends the protected response to EV
16. EV verifies session, freshness, operation, limit, validity,
    AuthToken and HMAC/AEAD protection
17. If valid + ACCEPT, EV performs the authorized CHARGE/DISCHARGE operation
18. If any check fails, operation is rejected
```

## M. Final Research Story for Astra

The final paper should present the contribution as:

\[
\boxed{
\text{QSKA Privacy-Preserving Authentication}
+
\text{2-of-3 Verifiable QSS Authorization}
+
\text{Context Binding}
+
\text{Fine-Grained CHARGE/DISCHARGE Authorization}
+
\text{Session-Bound Authenticated Response}
}
\]

The core distinction is:

> **QSKA answers whether the EV/CS are legitimate participants; QSV2G's threshold QSS layer answers whether enough independent authorities authorize this exact operation in this exact session.**

Astra should preserve this architecture and should not replace it with a different threshold-signature, blockchain, Hyperledger, or purely post-quantum architecture unless that is separately requested.
