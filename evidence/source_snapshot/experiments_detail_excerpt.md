## 2026-10-19T12:30:00-04:00   ACCEPTED (round 2) — camera-ready campaign opened
**Why:** User delivered round3(1).zip via WeChat: final round-2 reviews + the as-submitted R2 PDFs + NEED-TO-DO (camera-ready resolving ALL comments with minimal changes; plus project website + NEW clean public GitHub repo).
**Command(s):**
```bash
unzip round3(1).zip -> camera_ready/round3_inbox/round3/
# reviews were screenshots inside the docx: unzipped word/media/image{1..4}.png and read them
pdftotext -layout r2submit/1586_*.pdf  # structure + table extraction
```
**Output digest:**
- Decision: Accept in round 2 (AC P567, 2026-10-06). Scores: NMPy 5 WA (conf 3), izcJ 5 WA (conf 3), 6bih 4 BA (conf 4).
- Headline remaining concern (6bih + AC): GMFCS participant overlap acknowledged but "not resolved through corrected splits and rerun experiments".
- Other asks: release/licensing statement (NMPy), Table4-vs-Table7 number confusion (NMPy), PATHOGAIT SFT without vff (NMPy), Sec-3.1 source-sequence reformulation + 32-frame normalized-view clarity (izcJ), qualitative supp examples with skeleton viz + prompts + outputs (izcJ).
- As-submitted R2 = 11pp main / 18pp supp, a REWRITTEN manuscript vs our tree (10/16pp): new Fig 1, restructured tables, LOSO in main. Number reconciliation: submitted Tables 2/4/5/6 match our run JSONs cell-for-cell; abstract "0.76 vs 0.35" = ref .763 vs 7B exact-feature .347. Same lineage, different prose. We LACK the submitted tex (not in WeChat files or local trees) -> user must get it from Kaiyuan/Overleaf.
- Workspace: camera_ready/00_reviews_round2_final.md (full transcription), 01_camera_ready_action_map.md (comment->action map A1-A9, experiments E1-E5, website/repo plan, user-only items).
**Observation:** Unblocked now: E1 GMFCS corrected-split references (local), E3 leak-free zero-shot re-score (local), E4 PATHOGAIT SFT minus vff (torch), E5 qualitative panel (local), repo/website scaffold. Blocked on user: submitted tex, camera-ready instructions/deadline, author order, public-repo owner/name.

## 2026-10-19T13:40:00-04:00   Camera-ready A1: GMFCS corrected-split RERUN — E1 references + E3 roster rescore done, E2 SFT submitted
**Why:** 6bih + AC headline concern: GMFCS leak "not resolved through corrected splits and rerun experiments". Infrastructure existed (make_subject_splits.py `_sd` repair: train_sd 1602 / val_sd 478 / test_sd 866, 166 test patients; registry already freezes gmfcs to `_sd`).
**Command(s):**
```bash
# E1: references RETRAINED on corrected split (torch login, rs-qwen-env)
python code/cr_gmfcs_sd_references.py --features-dir .../dataset_0_GMFCS/features \
  --subject-map .../extracted_with_metadata/subject_map.json  # -> results/cr_gmfcs_sd_references.json
# E3: cached 5-model zero-shot re-parsed (anchored parser) + re-scored on test_sd
python code/cr_gmfcs_sd_rescore.py   # -> results/cr_gmfcs_sd_rescore.json
# E2: SFT retrained on train_sd; patched make_sft_data.py to resolve frozen splits
# (it took split names literally -> would have TRAINED on the leaked original train
#  even though view_run eval resolves to test_sd; one-line registry.split_name fix)
sbatch --export=ALL,DS=gmfcs sft_qwen7b.sbatch   # JID 20252461 (also re-evals zero-shot 7B on test_sd)
```
**Output digest:**
- E1 corrected split (1602->866, 166 subj): LR .4607/.3952/k.2409, SVM .4919/.4121/k.2708, RF mF1 .4155, maj mF1 .1312, chance .2498. Original split reproduces Table 4 (.452/.387 LR, .492/.410 SVM): leak removal moves LR +.008 mF1, SVM +.002.
- E3 checksum: full-899 reproduces submitted Table 2 GMFCS row cell-for-cell (.3515/.2098/.0177 llama ... .3693/.2182/.0325 qwen72; top-class .72/.78/.87/.93/.64). test_sd-866: llama .3533/.2122/.0249, qwen72 .3718/.2216/.0426, gemma .3129/.1634/.0299, glm .2691/.1266/-.0001, dsr1 .3106/.1905/.0145 - all moves <= .004 mF1, 0 invalid.
- make_sft_data.py frozen-split patch uploaded to torch (and the leak it prevents is itself ELN-worthy: SFT would have silently trained on leaked train).
**Observation:** The corrected-split story is complete except SFT (E2 running): every number moves marginally and conclusions are unchanged — exactly what camera-ready needs to answer 6bih/AC with "rerun, not re-score". Next: E2 result, E4 (PATHOGAIT SFT minus vff), E5 (qualitative panel; skeleton_imgs/gmfcs already on torch).

## 2026-10-19T15:10:00-04:00   E2 resubmitted 1-GPU + E4 (PATHOGAIT SFT minus vff) submitted
**Why:** torch queue saturated by other projects' jobs under QOSMaxGRESPerUser (2 GPU/user); the 2-GPU E2 (20252461) had no path to start -> cancelled OUR job and rebuilt both camera-ready SFT jobs as 1-GPU (7B LoRA + TP1 serving fits one H200 easily; backfills far better).
**Command(s):**
```bash
scancel 20252461   # ours
# choices patches: view_run.py + make_sft_data.py accept view "feature_vector_novff"
# new: make_novff_view.py (strips the valid_frame_fraction line from feature_vector
#      view text per split; asserts every row had it), cr_sft_featnovff.sbatch (1 GPU:
#      novff view -> SFT data -> LoRA train -> eval SFT + zero-shot-7B control on the
#      novff view), cr_sft_gmfcs_1gpu.sbatch (sed-derived from sft_qwen7b.sbatch).
sbatch --export=ALL,DS=gmfcs cr_sft_gmfcs_1gpu.sbatch        # JID 20259080 (E2)
sbatch --export=ALL,DS=pathological cr_sft_featnovff.sbatch  # JID 20259081 (E4)
```
**Output digest:** both PENDING behind QOSMaxGRESPerUser backlog (~50 jobs from alm/medvqa/expvid sessions — none touched). E4 also yields a bonus control: zero-shot 7B exact-feature minus vff.
**Observation:** vff field name verified as `valid_frame_fraction` in the pathological feature_vector view text. Kinematics-only reference for comparison: LR 0.564 (Fan B11 leave-one-out). Next: E5 qualitative assets from cached runs + skeleton_imgs.

## 2026-10-19T16:30:00-04:00   E5 qualitative assets complete (izcJ A7): 3 examples picked + rendered
**Why:** izcJ asked for supp qualitative analysis: skeleton visualization + model-visible input + verbatim LLM output, success and failure cases.
**Command(s):**
```bash
# cr_qualitative_pick.py (torch): picks from CACHED runs only
#   gmfcs_zs_fail_sft_fix: id=test_22, true GMFCS III, zero-shot(72B)->II (anchored parse), SFT(7B)->III; test_sd skeleton PNG
#   pathogait_zs_fail:     id=test_290, true "normal gait", zero-shot(72B) wrong
#   ataxia_sft_success_minority: id=test_11, true normal (minority), zs(72B)->"cerebellar ataxic gait", SFT(7B)->"normal gait"
# cr_render_clip.py (new): per-frame hip-centered montage, shared scale; --plane xz for
#   z-up Kinect data; Kinect-25 spine/arm bone connectivity completed
bash ~/rr.sh  # renders -> ~/cr_qual/*.png -> camera_ready/qualitative/
```
**Output digest:**
- First picker version had a SUBSTRING bug ("GMFCS III" contains "GMFCS II") that selected a CORRECT prediction as the "failure" — the paper's own parser lesson, caught by reading the raw output; fixed with the boundary-anchored parser.
- Original VLM-era renders unusable for ataxia/pathological (global frame + subject translation -> dots); clip-290 axis probe showed this Kinect export is Z-UP (head z=1.62 vs ankle z=0.22), y=depth -> xz plane, no flip.
- Final panels verified at full resolution: GMFCS side-view (good), ATAXIA 12-joint lower-body stride (good), PATHOGAIT frontal full skeleton with leg-cross at frame 76 (good).
- Bundle: camera_ready/qualitative/{3 png + qualitative_examples.json} (summary text + raw outputs included for the supp verbatim blocks).
**Observation:** A7 assets ready; the supp figure/tex block gets written once the submitted tex arrives. E2 (20259080) and E4 (20259081) still queued behind QOSMaxGRESPerUser backlog.

## 2026-10-19T19:30:00-04:00   Camera-ready text edits wave 1 on the submitted source (cr_tree)
**Why:** Submitted R2 tex arrived (GaitEval_WACV_Final_Final zip; body verified identical to r2submit PDF). Executed A6, A1(tables), A3, A2, A5, A7 on camera_ready/cr_tree.
**Command(s):** edits in cr_tree/sec/{3_benchmark,4_evaluation_conditions,5_protocol_metrics}.tex, supplementary.tex; scripts/make_qualitative_tex.py (mechanical JSON->tex); builds via pdflatex+bibtex.
**Output digest:**
- A6 (izcJ-W1): Sec 3.1 now defines the 124-frame sequence as the SOURCE never shown directly; Sec 3.2 states each view's structure (raw=full 124f; normalized=canonical 12-joint, centered/scaled, 32-frame subsample — verified in make_normalized_view.py; summary/features collapse). Also fixed a latent naming collision ("normalized view" meaning z-scored features).
- A1: Table 2 GMFCS row -> corrected-split re-scores (.353/.212/.025 ... .311/.191/.015, footnote c); Table 4 GMFCS row -> RETRAINED refs (LR .461/.395/.241, SVM .492/.412/.271, n=866); supp table "GMFCS original vs corrected" added (incl. verified original RF .515/.425/.272 — first draft had an UNVERIFIED RF row, caught and replaced with JSON values). Ladder row deferred until E2 lands (whole-row swap, never mixed splits; TODO comment in place).
- A3 (NMPy-W3): standardized-analysis intro + Table 7 caption now state explicitly why GMFCS carries different numbers in Tables 4 vs 7 (rebuilt corpus, different splits/features; neither replaces the other).
- A2 (NMPy-W2): new Sec 3.7 "Release and Licensing": no source pose redistribution, upstream licenses retained, what ships (split indices incl corrected GMFCS, generators, prompts, parser, raw generations, scoring, data contract) at github.com/james20141606/GaitEval.
- A5 (NMPy-W1): conclusion limitation extended with the standardized larger cohorts (149 GMFCS / 24 CARE-PD test participants).
- A7 (izcJ-W2): supp S.12 "Qualitative Examples" (3 skeleton montages + byte-identical model-visible summaries + verbatim outputs). CAUGHT: stored view files carry an internal "label: .../sample_index: ..." header that view_run redacts at load; first build printed the TRUE LABEL inside a "model-visible" block. Generator now replicates view_run._redact_leak exactly; leak-scan over the built PDF: 0 unredacted label fields, 4 [REDACTED].
- Builds: main 11pp (body still ends p8, refs p8-11), supp 20pp; both 0 errors / 0 ?? / 0 overfull.
- Also discovered sec/10_supplementary.tex is vestigial in this tree (real supp = supplementary.tex via supplementary_standalone.tex); a first insertion into the wrong file was reverted.
**Observation:** All text-side reviewer items are now in except the ladder row + vff sentence (E2/E4, both queued). Remaining: A8 full audit, A9 final-mode formatting, website+repo population.

## 2026-10-19T21:40:00-04:00   E2/E4 migrated to bigpurple (user request: shorter queue) — JID 28603768/28603769
**Why:** torch scheduler projected tomorrow-noon start for our 1-GPU jobs (same-account deep queue from other projects). User directed: use bigpurple.
**Command(s):**
```bash
# torch (CPU): build both SFT datasets; gmfcs auto-resolves to _sd via patched make_sft_data
#   gmfcs 1602/478/866; pathological_feature_vector_novff 7361/1327/2181
# bundle (sft_data + sft_train.py, 1.5MB) -> Mac -> bigpurple (fast; no big relay)
# bigpurple: venv --system-site-packages over /gpfs/scratch/cl6707/envs/vllm011
#   (vllm 0.11.0, torch 2.8.0+cu128, transformers 4.56.2) + pip trl==0.11.4 peft==0.13.2
#   (pinned to torch flare-2026 versions; transformers 4.56.2 vs 4.57.3 drift noted)
# Qwen2.5-7B-Instruct snapshot a09a354... downloaded on-cluster in 92 s (same hash as torch)
# new: code/bp_eval.py (self-contained anchored-parser eval against vLLM endpoint;
#   SFT test.jsonl carries the EXACT benchmark prompts so no registry port needed)
# cr_bp_sft.sbatch: train (v1 recipe) -> serve merged -> eval -> serve base -> zs eval
sbatch --export=ALL,DS=gmfcs cr_bp_sft.sbatch                              # 28603768
sbatch --export=ALL,DS=pathological_feature_vector_novff cr_bp_sft.sbatch  # 28603769
```
**Output digest:** partition notes: no gl40s on this cluster (CLAUDE.md stale); gpu4_*/gpu8_* are V100 (no bf16) -> a100_short (A100-80G). Both jobs submitted; F5 VPN dropped right after (jobs unaffected). torch fallback jobs 20302491/20302492 left queued (first result wins; the other gets cancelled).
**Observation:** Blocked on VPN re-auth (user double-click Connect.command) to collect results; expect train+both-evals well under an hour per dataset on A100.

## 2026-10-19T23:30:00-04:00   E2+E4 complete on bigpurple; A1 and A4 CLOSED in cr_tree
**Why:** bigpurple JIDs 28603768 (GMFCS corrected-split SFT, 15m35s) and 28603769 (PATHOGAIT vff-free feature-view SFT, 55m33s) COMPLETED; integrate and close the two remaining experiment-backed reviewer items.
**Output digest:**
- E2 GMFCS (train_sd->test_sd, n=866, 0 unparsed): SFT .373/.2585/k.0431 vs original-train SFT .363/.255/.030 (+.004 mF1; same eval subset) — conclusion unchanged, SFT stays below refs (.395/.412). 7B zero-shot cross-stack check on bigpurple: .2587/.1129/-.0089 vs torch .249/.110/-.008 (within ~.003 mF1; serving-stack noise). KEY CATCH: the submitted ladder/Table-3 7B cells were ALREADY evaluated on the corrected subset (view_run frozen-split) — swapping in the bigpurple re-measure would have created a new Table-3-vs-ladder inconsistency; reverted to the torch value, only the SFT cell (true retrain) and zs-72B re-score changed. Ladder GMFCS row now: .222/.043 | .110/-.008 | -- | .259/.043 | -- | .412 | .395.
- E4 PATHOGAIT vff-free (n=2181, 0 unparsed): SFT .641/.6316/k.5649 vs with-vff .687/.611(k) [mF1 .687]; zero-shot on vff-free view fully collapsed (.11/.033/0, all "normal gait"). Integrated: vff paragraph now states the rerun (~.05 mF1 tracks capture signal; mapping does not depend on it; still above kinematics-only refs .564/.560). NMPy-W4 closed.
- Also fixed: the GMFCS corrected-split supp table had been inserted into vestigial sec/10_supplementary.tex (not built); moved into supplementary.tex with the SFT row + eval-set footnote.
- Builds: main 11pp (refs from p8), supp 21pp; 0 errors/??/overfull. torch fallback jobs 20302491/92 cancelled.
**Observation:** All experiment-backed reviewer items (A1, A4) now closed. Remaining: A8 full audit, A9 de-anonymization (needs author 3/4 order + CR email), repo+website.

## 2026-10-20T10:30:00-04:00   A8 audit pass: stale-number sweep, corrected-split paired test, 2 swallowed sentences, page-limit restore
**Why:** Numbers final after E2/E4 -> full consistency audit of the camera-ready tree before formatting.
**Output digest:**
- Stale GMFCS sweep found original-split values left in: Table 1 (claimed "leakage-free" but listed 1574/473/899 — an internal contradiction already present in the SUBMITTED R2), supp core-refs table (incl. class_weight=None column), supp zero-shot full table, supp ladder. All moved to corrected split (Table 1 now 1602/478/866; refs none-weighted .418/.400 from cr_gmfcs_sd_references.json).
- Corrected-split paired subject bootstrap recomputed (code/cr_gmfcs_paired.py): SFT-LR = -0.137 [-0.186,-0.085], p=0.001, 166 participants (was -0.132/174). Independent cross-check: supp participant-level table already reported corrected LR 0.395 [0.350,0.438] / 166 — matches E1 CI digit-for-digit.
- Kept on purpose: ordinal table + Table 7 GMFCS rows belong to the standardized corpus (255/149); 7B view-comparison rows already on the corrected subset (^s).
- SWALLOWED-COMMENT BUG x2 (my own CR comments placed mid-line): conclusion lost its final "Overall, GaitEval shows ..." sentence; supp lost the PARKINSONISM-SFT interval sentence. Fixed by line-breaking after every "% [CR ...]"; grep clean; both sentences verified in PDFs.
- Page limit: restored sentences + CR additions pushed Table 7 (table*) and the conclusion tail onto p9 after References. Fixed by relocating the Table-7 source right after the transfer table (keeps numbering 6->7) and tightening the conclusion (removed a duplicated two-participant caveat and one restating sentence; no claim change). Main: body ends p8, p9 starts with References; supp 21pp; 0 errors/??/overfull.
**Observation:** Camera-ready text content complete pending A9 (author block: need 3rd/4th order + affiliations/emails; CR email for final-mode/copyright). Bib unchanged since Kaiyuan's pre-submission citation audit (no new \cite added in CR).

## 2026-10-20T15:00:00-04:00   Public repo populated + verified; 3 more paper defects caught by the reproduction harness
**Why:** NEED-TO-DO #2 requires a NEW public repo whose code reproduces the paper's results. Built camera_ready/GaitEval_public (own git, excluded from this repo) and verified it end-to-end.
**Command(s):**
```bash
python code/build_public_release.py      # curated 35 files + paths.py; rewrites every private path to $GAITEVAL_ROOT; GATE: fails on any xc1490/cl6707/scratch/Users string
# functional test on torch with an isolated GAITEVAL_ROOT (symlinks to real data):
#   cr_gmfcs_sd_references.py / cr_gmfcs_sd_rescore.py / cr_gmfcs_paired.py / feature_baseline.py
python scripts/score_table2.py && python scripts/verify_repro.py   # local, predictions/ only
```
**Output digest:**
- Public code reproduces, digit-for-digit: Table 4 all rows (ATAXIA .778/.763, PARK .625/.613, PATHO .659/.662, RF .848/.689), GMFCS corrected refs (.461/.395/.241, SVM .412), Table 2 corrected GMFCS row, paired SFT-LR -0.1367. verify_repro: 23/23 on torch (data-dependent) + 60/60 locally from predictions/ alone = 83 checks.
- predictions/: 21 v1 zero-shot runs (incl. PARKINSONISM/Llama archived as abl_motionsum_*), SFT/few-shot/structured/OOD runs, CR reruns, v2.1 runs; 23 MB; zero private paths. splits/: subject maps x4 + GMFCS *_sd TSVs + test_sd id list.
- Harness caught (paper side, all fixed in cr_tree): (1) MY CR rounding error: GMFCS DeepSeek corrected kappa 0.01449 printed 0.015 -> 0.014 (3 places); (2) SUBMITTED-version rounding error: PATHOGAIT Qwen72B macro-F1 0.054506 printed 0.054 -> 0.055 (5 places: Table 2, ladder Table 5, Sec 4.5 prose, 2 supp tables); (3) Sec 4.2 + supp kappa range "-0.069 to 0.035" stale after the GMFCS split correction -> "-0.069 to 0.043" (Qwen GMFCS corrected kappa .043). Full Table 2 audit: 60 printed values vs exact: only these 2 mismatches.
- Convention made explicit in the scorer: paper macro-F1 = sklearn label-union (unparsed -1 enters as extra zero-F1 class; PATHOGAIT Llama/GLM average over 7 labels) — scorer reproduces .053/.059 only under this rule.
- Docs: README, docs/REPRODUCE.md (per-table map), docs/DATASETS.md (official sources + license status from the v2.1 delivery report: PARKINSONISM CC BY-NC-ND 4.0; PATHOGAIT no explicit license -> link only), MIT LICENSE (code/outputs only), requirements.
- Paper rebuilt: body ends p8, p9 starts with References; 0 ??/overfull.
**Observation:** Repo is local-only (git 65dbcd0), NOT pushed: creation on GitHub (private first) + going public need the user's go. README citation author order has a TODO until 3rd/4th author confirmed. Website next.

## 2026-10-20T16:10:00-04:00   Project page built (GaitEval_public/website) + Pages workflow; local only
**Why:** NEED-TO-DO #2 project website.
**Output digest:**
- Single-file Nerfies-style page: title/authors/buttons, Fig 1 teaser, abstract (submitted text), 3 key-finding cards, benchmark + view definitions (source-sequence framing), Table 2 (all 20 cells, corrected GMFCS), references+adaptation table, 3 qualitative cases with verbatim outputs, reproduce snippet, BibTeX.
- Every number cross-checked against the camera-ready tables/verify_repro. Figure3.png and fig4 (zero-shot gap / ladder plots) deliberately NOT used: they are absent from the CR build and still carry original-split GMFCS values.
- One wording fix after render review: transfer "at or below target-majority in both directions" was wrong for ATAXIA->PATHOGAIT macro-F1 (.496 > .471); now states accuracy + kappa precisely.
- .github/workflows/pages.yml deploys website/ via Actions on push.
- Rendered with headless Chrome; layout verified.
**Observation:** public repo commits 2349936..886dbf4 local only. Going live needs: user OK to create james20141606/GaitEval (private first), 3rd/4th author order, Pages enablement.

## 2026-10-21T18:30:00-04:00   GaitEval public repo LIVE; paper switched to camera-ready (final) mode
**Why:** User: make james20141606/GaitEval public directly; forwarded the CPS camera-ready email; Jiangpeng He is corresponding author.
**Command(s):**
```bash
gh repo create james20141606/GaitEval --public ...; git push   # GaitEval_public main
gh api -X POST repos/james20141606/GaitEval/pages -f build_type=workflow; gh workflow run pages.yml   # deploy: success
# camera-ready instructions doc (Google Doc export) read in full
# main.tex: [review,datasets] -> [final,datasets]; axessibility (+accsupp generated from CTAN .dtx, not in local TeX); paper ID 1586; author block
```
**Output digest:**
- Repo PUBLIC: https://github.com/james20141606/GaitEval (leak scan clean before push). Pages deploy succeeded BUT site unreachable: user-site repo james20141606.github.io has Pages custom domain www.cmwonderland.com whose DNS is on Vercel (cname.vercel-dns.com) -> every project page redirects to Vercel -> 404. Not touched (other repo / user's domain).
- Official CR instructions (differ from the public AuthorGuides page): camera-ready deadline Nov 4 2026 11:59 PM PDT (incl. supp); AUTHOR REGISTRATION by Nov 2 11:59 PM MDT or paper excluded; no page numbers; 8pp body; author list must exactly match OpenReview (no changes/reorders); supp file name 01586_supp (PDF/ZIP <=200MB); PDF eXpress Conference ID 68687X; possible final AI/hallucinated-reference check; only the authorized contact (ky20@iu.edu = Kaiyuan) can submit.
- Final build: body ends p8, References from p9; no review header/line numbers/page numbers; main 22 fonts all embedded, 0 Type 3. Supp: 12 Type 3 fonts from figure PDFs (supp is not PDF-eXpress-validated, acceptable). Staged camera_ready/submission/{01586_main_cameraready.pdf, 01586_supp.pdf}.
- Author block: Kaiyuan Yang^1 (Indiana University, ky20@iu.edu), Xupeng Chen^2 (NYU, xc1490@nyu.edu), Fan Huang^3, Jiangpeng He^4,* — affiliations/emails for 3/4 are red placeholders (not guessed). Order must be verified against OpenReview (an older internal note listed Kaiyuan, Fan, Xupeng, Jiangpeng).
**Observation:** Remaining = user/Kaiyuan only: affiliations+emails, OpenReview order check, author registration, Pages domain fix, Kaiyuan's PDF eXpress + copyright + upload.

## 2026-10-21T20:10:00-04:00   Plan C live: gaiteval org — code repo transferred, project page at gaiteval.github.io
**Why:** User chose plan C (org) after the user-site custom domain (Vercel) broke project Pages under james20141606.
**Command(s):**
```bash
gh api -X DELETE repos/james20141606/GaitEval/pages
gh api -X POST repos/james20141606/GaitEval/transfer -f new_owner=gaiteval
gh repo create gaiteval/gaiteval.github.io --public ; git push (via ssh.github.com:443; port 22 reset)
gh repo edit gaiteval/GaitEval --homepage https://gaiteval.github.io
```
**Output digest:**
- https://gaiteval.github.io -> 200, title OK, teaser asset 200, Code button -> github.com/gaiteval/GaitEval.
- https://github.com/gaiteval/GaitEval PUBLIC; old URL github.com/james20141606/GaitEval redirects (200).
- Paper (Sec 3 Release and Licensing) + README already point to github.com/gaiteval/GaitEval and gaiteval.github.io.
**Observation:** Website + repo deliverable (NEED-TO-DO #2) done. Remaining user/Kaiyuan items: affiliations/emails for Fan Huang + Jiangpeng He, OpenReview author-order check, author registration by Nov 2 MDT, Kaiyuan's PDF eXpress (68687X) + copyright + upload by Nov 4 PDT.

