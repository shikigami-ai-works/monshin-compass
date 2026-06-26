# K-Dense-AI/scientific-agent-skills 全力分析

作成日: 2026-06-25  
対象: https://github.com/K-Dense-AI/scientific-agent-skills  
確認コミット: `9c9bd2e92af12311ecd0c1a643e0931643f9ea04`  
確認方法: GitHub README, GitHub API, raw `SKILL.md`, raw `SECURITY.md`, workflow YAML の read-only intake。clone、install、実行はしていない。

## 結論

`K-Dense-AI/scientific-agent-skills` は、科学・医療・バイオ・化学・データ分析向けの「エージェント用スキル百科」としては非常に強い。

ただし、問診コンパスに対しては **丸ごと導入しない** 判断が正しい。理由は、医療・臨床系スキルの一部が直接的な治療計画、臨床判断支援、外部API送信、Bash実行、ファイル生成、APIキー利用を含み、repo自身の `SECURITY.md` でも Critical/High が多数出ているため。

採用するなら、実行物ではなく **設計パターンだけを抽出してローカルに再実装** する。

## 観測した事実

| 項目 | 値 |
|---|---:|
| Stars | 29,222 |
| Forks | 2,976 |
| Open issues/PRs | 35 |
| Latest release | `v2.53.0`, 2026-06-23 |
| Default branch | `main` |
| License | MIT |
| Repository size | 36,296 KB |
| Tree paths | 1,910 |
| Skill count | 147 |
| Skills with `scripts/` | 70 |
| Skills with `references/` | 135 |
| Skills with `assets/` | 24 |
| Security scan findings | 877 |
| Critical skills | 21 |
| High skills | 20 |
| Safe skills in own scan | 106 / 147 |

## 何が強いか

1. **科学系ワークフローの分解がうまい**
   - `database-lookup`, `paper-lookup`, `scientific-critical-thinking`, `statistical-analysis` など、研究者がやる作業を「検索」「取得」「評価」「報告」に分けている。
   - 問診コンパスでも、症状入力を「絞り込み」「緊急度」「根拠確認」「医師に伝える要約」に分ける設計と相性がよい。

2. **database-lookup の retrieval contract はかなり参考になる**
   - 取得対象、識別子、日付、フィルタ、ページング、件数照合、出典、警告を明示する思想がある。
   - 医療RAGでありがちな「それっぽい根拠説明」を避けるために使える。

3. **外部データを untrusted data と見る姿勢がある**
   - API応答内の指示に従わない、raw payload をそのまま扱わない、秘密情報を出力しない、という方針が `database-lookup` に入っている。
   - 問診コンパスのRAGにも必須。

4. **CIでPR時スキルスキャンをしている**
   - `.github/workflows/pr-skill-scan.yml` は変更されたスキルをスキャンし、`--fail-on HIGH` でブロックする設計。
   - これは良い運用品質シグナル。

5. **更新速度が速い**
   - 2026-06-23 に `v2.53.0` が出ており、直近コミットもある。
   - 生きているrepoではある。

## 致命傷候補

### 1. Critical/High が現行mainに残っている

repo自身の `SECURITY.md` は 2026-06-22 時点で、147スキル中 877 findings、Critical 66 findings、High 48 findings、Critical分類スキル21、High分類スキル20を示している。

影響:
- 「スキャンがある」ことは「安全」ではない。
- 問診コンパスに丸ごと入れると、医療文脈で外部通信、APIキー、Bash、ファイル生成が混ざる。

潰し方:
- 全体導入は禁止。
- 1スキルずつ docs-only で読み、ローカル仕様に再構成する。

今やるべきか:
- 今すぐ。最初に境界を決めないと、あとでスキル導入が事実上の設計支配になる。

### 2. clinical-decision-support / treatment-plans は問診コンパスに直採用不可

`clinical-decision-support` と `treatment-plans` は、どちらも `Read Write Edit Bash` を許可し、外部APIを使うAI図生成を文書に組み込む設計になっている。`SECURITY.md` では両方 Critical。

特に `treatment-plans` は「個別患者の治療計画」に寄っており、問診コンパスの「症状整理・受診判断補助」と目的が違う。

影響:
- 診断・治療っぽさが増え、規制・安全・UXリスクが跳ねる。
- ユーザーが受診を遅らせる誤った安心につながる。

潰し方:
- 直採用しない。
- 使うなら「文書構成」「SMART goals」「根拠表示」の発想だけ抽出。
- 問診コンパスでは治療計画を生成しない。

今やるべきか:
- 今すぐ禁止リストに入れる。

### 3. mandatory schematic 文化は危ない

複数のスキルが、AI図生成を必須または強く推奨している。これにより外部API呼び出し、APIキー、コスト、未公開情報送信がワークフローに紛れ込む。

影響:
- 問診データや医療文脈を外部送信する事故につながる。
- ユーザーが「ただ結果を見たい」だけでも外部API消費が発生しうる。

潰し方:
- 問診コンパスでは図生成は完全に別ゲート。
- 症状イラストは静的・ローカル・レビュー済み素材にする。
- LLMに患者入力を画像生成APIへ送らせない。

今やるべきか:
- 今すぐ。UI素材設計に関わる。

### 4. 医療・臨床の強い語彙が多すぎる

スキル群には clinical, treatment, patient, HIPAA, CDS, treatment recommendation などが広く出る。これは研究・製薬向けには強いが、一般ユーザー向け問診ナビには強すぎる。

影響:
- UIの文言が診断・治療・医療判断支援に寄る。
- 「これは医師向けの支援なのか、患者向けなのか」が曖昧になる。

潰し方:
- 問診コンパスの語彙を固定する。
- 使用可: 症状整理、緊急サイン、受診相談、医師に伝えるメモ、根拠。
- 使用禁止: 診断確定、治療推奨、処方提案、個別治療計画、予後断定。

今やるべきか:
- 今すぐ。プロダクト名・画面文言・RAGプロンプトに直結する。

## 問診コンパスに転用できるパターン

| 元repoの要素 | 判定 | 問診コンパスでの使い方 |
|---|---|---|
| `database-lookup` の retrieval contract | Adapt | 根拠検索の契約として再実装。API名、条件、取得日、件数、失敗を必ず出す |
| `paper-lookup` のDB選択表 | Adapt | 医療情報源の選択表にする。MedlinePlus、CDC、FDA、MHLW等を分ける |
| `scientific-critical-thinking` の evidence grading | Adapt | RAG回答の根拠強度・未検証・境界条件チェックに使う |
| `statistical-analysis` の test selection | Later | 症例データ解析フェーズで使う。初期MVPでは不要 |
| `clinical-decision-support` | Reject direct | 医師・製薬・研究者向けすぎる。文書構成だけ参考 |
| `treatment-plans` | Reject direct | 個別患者の治療計画は問診コンパスの非目標 |
| `pyhealth` | Later / gated | EHR/臨床ML用途。今は実データも承認もない |
| `scientific-schematics` 系 | Reject direct | 外部画像生成・APIキー・コストが混ざる。症状イラストは別設計 |

## 問診コンパスへの推奨アーキテクチャ修正

K-Dense型の「巨大スキル集をエージェントに読ませる」方式ではなく、問診コンパスでは以下の4層に分ける。

1. Symptom Card Layer
   - 症状イラスト、部位、強さ、期間、発症タイミング。
   - LLMを入れない。

2. Safety Rule Layer
   - red flag、年齢、妊娠、既往、意識、呼吸、胸痛、出血など。
   - ルールベース。LLMに判断させない。

3. Evidence Retrieval Layer
   - 普通検索 + RAG。
   - database-lookup型の retrieval contract を採用。
   - 出典、取得日、更新日、回答不能を必ず残す。

4. Explanation Layer
   - LLMは説明整形だけ。
   - 診断、治療、処方、受診不要判断は禁止。

## 採用判断

総合判定: **Do not install. Adapt patterns only.**

理由:
- 147スキル全体は広く強いが、問診コンパスのMVPには広すぎる。
- Critical/Highスキルが現行mainに残っている。
- 医療系スキルは「一般ユーザーの症状整理」ではなく「専門文書・治療計画・臨床研究」に寄る。
- 外部API、Bash、Write/Edit、APIキーが絡むスキルが多い。

採用してよいもの:
- retrieval contract
- provenance-first output
- evidence-quality checklist
- untrusted external response handling
- source selection guide の作り方

採用してはいけないもの:
- `npx skills add`
- `gh skill install`
- `git clone` による丸ごと導入
- clinical/treatment系スキルの直用
- mandatory external image generation
- API keyが絡むスキルの自動起動
- Bash/curl前提の検索フロー

## 次の30分タスク

`docs/evidence-retrieval-contract.md` を作る。

内容:
- 問診コンパスで使う情報源候補
- 情報源ごとの役割
- 検索入力の正規化
- 取得日、更新日、出典URL、引用可能範囲
- RAGに渡してよい本文量
- 外部データを untrusted と扱うルール
- red flag と根拠検索の優先順位
- 回答不能時の出力テンプレート

完了条件:
- `発熱・咳・息苦しさ` MVPで使える
- LLMが診断断定できない
- 情報源と根拠が追跡できる
- 外部repoを1行も実行・導入しない

## このレポートから得た経験値

1. 外部スキルrepoは、Star数より `SECURITY.md` と workflow を先に見る。
2. 「スキャン済み」は「安全」ではない。Critical/Highが残っているなら導入禁止。
3. 医療系エージェントスキルは、患者向けMVPには強すぎることが多い。
4. 使うべきなのはスキル本体ではなく、契約・評価・根拠・境界の設計パターン。
5. 問診コンパスでは、治療計画・臨床判断支援・外部API図生成を最初から非目標にする。

## 参照ソース

- Repository: https://github.com/K-Dense-AI/scientific-agent-skills
- README: https://raw.githubusercontent.com/K-Dense-AI/scientific-agent-skills/main/README.md
- SECURITY.md: https://raw.githubusercontent.com/K-Dense-AI/scientific-agent-skills/main/SECURITY.md
- PR scan workflow: https://raw.githubusercontent.com/K-Dense-AI/scientific-agent-skills/main/.github/workflows/pr-skill-scan.yml
- Weekly security scan workflow: https://raw.githubusercontent.com/K-Dense-AI/scientific-agent-skills/main/.github/workflows/security-scan.yml
- clinical-decision-support: https://raw.githubusercontent.com/K-Dense-AI/scientific-agent-skills/main/skills/clinical-decision-support/SKILL.md
- treatment-plans: https://raw.githubusercontent.com/K-Dense-AI/scientific-agent-skills/main/skills/treatment-plans/SKILL.md
- database-lookup: https://raw.githubusercontent.com/K-Dense-AI/scientific-agent-skills/main/skills/database-lookup/SKILL.md
- scientific-critical-thinking: https://raw.githubusercontent.com/K-Dense-AI/scientific-agent-skills/main/skills/scientific-critical-thinking/SKILL.md
- paper-lookup: https://raw.githubusercontent.com/K-Dense-AI/scientific-agent-skills/main/skills/paper-lookup/SKILL.md
