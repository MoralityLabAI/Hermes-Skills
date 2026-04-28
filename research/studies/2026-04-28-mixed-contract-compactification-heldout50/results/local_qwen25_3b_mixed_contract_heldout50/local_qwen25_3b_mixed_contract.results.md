# Local Qwen2.5-3B Mixed Contract Heldout50

Generated: `2026-04-28T16:54:35.147004+00:00`

Evidence class: `live_model_local_3b`

Model: `D:\Research_Engine\models\Qwen2.5-3B-Instruct-GGUF\qwen2.5-3b-instruct-q4_k_m.gguf`
llama.cpp completion: `D:\Research_Engine\tools\llama.cpp-b8922-cuda12.4\llama-completion.exe`
Peak child RSS: `2359.30 MB`

Full 50-row held-out local 3B run against frozen mixed-contract validators. This is live_model_local_3b evidence, not trained TRM lift.

## Arm Summary

| Arm | Rows | Contract valid | Semantic valid | Exact success | Exact rate |
| --- | ---: | ---: | ---: | ---: | ---: |
| `baseline` | 50 | 24 | 30 | 23 | 0.4600 |
| `metta_runtime` | 50 | 35 | 39 | 32 | 0.6400 |
| `metta_runtime_repair` | 50 | 39 | 42 | 37 | 0.7400 |
| `pure_trm` | 50 | 30 | 36 | 27 | 0.5400 |

## Case Detail

| Row | Family | Arm | Exact | Contract | Semantic | Output |
| --- | --- | --- | ---: | ---: | ---: | --- |
| `heldout_ifsum_001_climate` | `if_summarize_judge` | `baseline` | 0 | 0 | 0 | <code>Coastal warming confirmed by sensors.</code> |
| `heldout_ifsum_001_climate` | `if_summarize_judge` | `pure_trm` | 0 | 0 | 0 | <code>Coastal warming detected steadily</code> |
| `heldout_ifsum_001_climate` | `if_summarize_judge` | `metta_runtime` | 0 | 0 | 0 | <code>Coastal warming steady as sensed</code> |
| `heldout_ifsum_001_climate` | `if_summarize_judge` | `metta_runtime_repair` | 0 | 0 | 0 | <code>Coastal warming sensed steady</code> |
| `heldout_ifsum_002_robotics` | `if_summarize_judge` | `baseline` | 0 | 0 | 0 | <code>Charging docks failure delayed robots.</code> |
| `heldout_ifsum_002_robotics` | `if_summarize_judge` | `pure_trm` | 0 | 0 | 0 | <code>Robots delayed due to failed docks</code> |
| `heldout_ifsum_002_robotics` | `if_summarize_judge` | `metta_runtime` | 0 | 0 | 0 | <code>Warehouse robots delayed due to charging docks failure.</code> |
| `heldout_ifsum_002_robotics` | `if_summarize_judge` | `metta_runtime_repair` | 0 | 0 | 1 | <code>Warehouse robots delayed; charging docks failed.</code> |
| `heldout_ifsum_003_security` | `if_summarize_judge` | `baseline` | 0 | 0 | 1 | <code>Encrypted backups saved data post-outage.</code> |
| `heldout_ifsum_003_security` | `if_summarize_judge` | `pure_trm` | 0 | 0 | 0 | <code>Encrypted backups saved data loss</code> |
| `heldout_ifsum_003_security` | `if_summarize_judge` | `metta_runtime` | 0 | 0 | 1 | <code>Encrypted backups saved data post-outage</code> |
| `heldout_ifsum_003_security` | `if_summarize_judge` | `metta_runtime_repair` | 1 | 1 | 1 | <code>Encrypted backups saved data post-outage loss</code> |
| `heldout_ifsum_004_biology` | `if_summarize_judge` | `baseline` | 0 | 0 | 1 | <code>Protein assay showed enzyme stability enhancement.</code> |
| `heldout_ifsum_004_biology` | `if_summarize_judge` | `pure_trm` | 0 | 0 | 1 | <code>Protein assay improved enzyme stability</code> |
| `heldout_ifsum_004_biology` | `if_summarize_judge` | `metta_runtime` | 0 | 0 | 0 | <code>Protein assay confirmed improved stability</code> |
| `heldout_ifsum_004_biology` | `if_summarize_judge` | `metta_runtime_repair` | 1 | 1 | 1 | <code>Protein assay confirmed improved enzyme stability</code> |
| `heldout_ifsum_005_energy` | `if_summarize_judge` | `baseline` | 0 | 0 | 0 | <code>Solar microgrid powered early morning.</code> |
| `heldout_ifsum_005_energy` | `if_summarize_judge` | `pure_trm` | 0 | 0 | 0 | <code>Solar grid powered early morning</code> |
| `heldout_ifsum_005_energy` | `if_summarize_judge` | `metta_runtime` | 0 | 1 | 0 | <code>Solar microgrid powered up early morning</code> |
| `heldout_ifsum_005_energy` | `if_summarize_judge` | `metta_runtime_repair` | 1 | 1 | 1 | <code>Solar microgrid powered up before sunrise</code> |
| `heldout_ifsum_006_archive` | `if_summarize_judge` | `baseline` | 0 | 0 | 1 | <code>Archive index shows missing receipts.</code> |
| `heldout_ifsum_006_archive` | `if_summarize_judge` | `pure_trm` | 1 | 1 | 1 | <code>Missing receipts exposed in archive index</code> |
| `heldout_ifsum_006_archive` | `if_summarize_judge` | `metta_runtime` | 0 | 0 | 1 | <code>Archive index exposed missing receipts</code> |
| `heldout_ifsum_006_archive` | `if_summarize_judge` | `metta_runtime_repair` | 1 | 1 | 1 | <code>Archive index exposed missing migration receipts</code> |
| `heldout_ifsum_007_question_logic` | `if_summarize_judge` | `baseline` | 1 | 1 | 1 | <code>Could verifier gates cut invalid commits soon?</code> |
| `heldout_ifsum_007_question_logic` | `if_summarize_judge` | `pure_trm` | 1 | 1 | 1 | <code>Could verifier gates reduce invalid commits tomorrow?</code> |
| `heldout_ifsum_007_question_logic` | `if_summarize_judge` | `metta_runtime` | 1 | 1 | 1 | <code>Could verifier gates reduce invalid commits tomorrow?</code> |
| `heldout_ifsum_007_question_logic` | `if_summarize_judge` | `metta_runtime_repair` | 1 | 1 | 1 | <code>Could verifier gates reduce invalid commits tomorrow?</code> |
| `heldout_ifsum_008_question_data` | `if_summarize_judge` | `baseline` | 1 | 1 | 1 | <code>Can typed rows expose vulnerable validators?</code> |
| `heldout_ifsum_008_question_data` | `if_summarize_judge` | `pure_trm` | 1 | 1 | 1 | <code>Can typed rows reveal brittle validators?</code> |
| `heldout_ifsum_008_question_data` | `if_summarize_judge` | `metta_runtime` | 1 | 1 | 1 | <code>Can typed rows reveal brittle validators?</code> |
| `heldout_ifsum_008_question_data` | `if_summarize_judge` | `metta_runtime_repair` | 1 | 1 | 1 | <code>Can typed rows reveal brittle validators?</code> |
| `heldout_ifsum_009_question_tools` | `if_summarize_judge` | `baseline` | 0 | 0 | 1 | <code>Can schema memory enhance tool routing skills?</code> |
| `heldout_ifsum_009_question_tools` | `if_summarize_judge` | `pure_trm` | 1 | 1 | 1 | <code>Will schema memory improve tool routing?</code> |
| `heldout_ifsum_009_question_tools` | `if_summarize_judge` | `metta_runtime` | 1 | 1 | 1 | <code>Will schema memory improve tool routing?</code> |
| `heldout_ifsum_009_question_tools` | `if_summarize_judge` | `metta_runtime_repair` | 1 | 1 | 1 | <code>Will schema memory improve tool routing?</code> |
| `heldout_ifsum_010_question_repair` | `if_summarize_judge` | `baseline` | 1 | 1 | 1 | <code>Should repair gates block unsafe outputs?</code> |
| `heldout_ifsum_010_question_repair` | `if_summarize_judge` | `pure_trm` | 1 | 1 | 1 | <code>Should repair gates reject unsafe outputs?</code> |
| `heldout_ifsum_010_question_repair` | `if_summarize_judge` | `metta_runtime` | 1 | 1 | 1 | <code>Should repair gates reject unsafe outputs?</code> |
| `heldout_ifsum_010_question_repair` | `if_summarize_judge` | `metta_runtime_repair` | 1 | 1 | 1 | <code>Should repair gates reject unsafe outputs?</code> |
| `heldout_pyd_task_001` | `pydantic_adherence` | `baseline` | 0 | 0 | 0 | <code>{&quot;invoices&quot;: [{&quot;priority&quot;: &quot;high&quot;, &quot;due_date&quot;: &quot;2026-05-03&quot;, &quot;blocked&quot;: false}]}</code> |
| `heldout_pyd_task_001` | `pydantic_adherence` | `pure_trm` | 1 | 1 | 1 | <code>{\n  &quot;task&quot;: &quot;collect invoices&quot;,\n  &quot;priority&quot;: &quot;high&quot;,\n  &quot;due_date&quot;: &quot;2026-05-03&quot;,\n  &quot;blocked&quot;: false\n}</code> |
| `heldout_pyd_task_001` | `pydantic_adherence` | `metta_runtime` | 1 | 1 | 1 | <code>{&quot;blocked&quot;: false, &quot;due_date&quot;: &quot;2026-05-03&quot;, &quot;priority&quot;: &quot;high&quot;, &quot;task&quot;: &quot;collect invoices&quot;}</code> |
| `heldout_pyd_task_001` | `pydantic_adherence` | `metta_runtime_repair` | 1 | 1 | 1 | <code>{&quot;blocked&quot;: false, &quot;due_date&quot;: &quot;2026-05-03&quot;, &quot;priority&quot;: &quot;high&quot;, &quot;task&quot;: &quot;collect invoices&quot;}</code> |
| `heldout_pyd_task_002` | `pydantic_adherence` | `baseline` | 0 | 0 | 0 | <code>{&quot;task&quot;: {&quot;audit&quot;: {&quot;validators&quot;: {&quot;priority&quot;: &quot;medium&quot;, &quot;due_date&quot;: &quot;2026-05-04&quot;, &quot;blocked&quot;: false}}}}</code> |
| `heldout_pyd_task_002` | `pydantic_adherence` | `pure_trm` | 1 | 1 | 1 | <code>{\n  &quot;blocked&quot;: false,\n  &quot;due_date&quot;: &quot;2026-05-04&quot;,\n  &quot;priority&quot;: &quot;medium&quot;,\n  &quot;task&quot;: &quot;audit validators&quot;\n}</code> |
| `heldout_pyd_task_002` | `pydantic_adherence` | `metta_runtime` | 0 | 0 | 0 | <code>{&quot;env_family&quot;: &quot;pydantic_adherence&quot;, &quot;failure_labels&quot;: [&quot;json_parse&quot;, &quot;missing_field&quot;, &quot;enum&quot;, &quot;date&quot;], &quot;validator&quot;: {&quot;blocked&quot;: f</code> |
| `heldout_pyd_task_002` | `pydantic_adherence` | `metta_runtime_repair` | 0 | 0 | 0 | <code>{&quot;env_family&quot;: &quot;pydantic_adherence&quot;, &quot;failure_labels&quot;: [&quot;json_parse&quot;, &quot;missing_field&quot;, &quot;enum&quot;, &quot;date&quot;], &quot;validator&quot;: {&quot;blocked&quot;: f</code> |
| `heldout_pyd_task_003` | `pydantic_adherence` | `baseline` | 0 | 0 | 0 | <code>{&quot;freeze_prompts&quot;: [{&quot;prompt_id&quot;: 123, &quot;priority&quot;: &quot;high&quot;, &quot;due_date&quot;: &quot;2026-05-05&quot;, &quot;blocked&quot;: true}]}</code> |
| `heldout_pyd_task_003` | `pydantic_adherence` | `pure_trm` | 0 | 1 | 0 | <code>{\n  &quot;task&quot;: &quot;freeze_prompts&quot;,\n  &quot;priority&quot;: &quot;high&quot;,\n  &quot;due_date&quot;: &quot;2026-05-05&quot;,\n  &quot;blocked&quot;: true\n}</code> |
| `heldout_pyd_task_003` | `pydantic_adherence` | `metta_runtime` | 0 | 0 | 0 | <code>{&quot;env_family&quot;: &quot;pydantic_adherence&quot;, &quot;failure_labels&quot;: [&quot;missing_field&quot;], &quot;validator_result&quot;: {&quot;blocked&quot;: true, &quot;due_date&quot;: &quot;2026-05-05&quot;, &q</code> |
| `heldout_pyd_task_003` | `pydantic_adherence` | `metta_runtime_repair` | 0 | 0 | 0 | <code>{&quot;env_family&quot;: &quot;pydantic_adherence&quot;, &quot;failure_labels&quot;: [&quot;missing_field&quot;, &quot;enum&quot;], &quot;validator_result&quot;: {&quot;blocked&quot;: true, &quot;due_date&quot;: &quot;20</code> |
| `heldout_pyd_task_004` | `pydantic_adherence` | `baseline` | 0 | 0 | 0 | <code>{&quot;label&quot;:&quot;task label failures&quot;,&quot;priority&quot;:&quot;medium&quot;,&quot;due_date&quot;:&quot;2026-05-06&quot;,&quot;blocked&quot;:false}</code> |
| `heldout_pyd_task_004` | `pydantic_adherence` | `pure_trm` | 0 | 0 | 0 | <code>{\n  &quot;task_label_failures&quot;: [\n    {\n      &quot;task&quot;: &quot;str&quot;,\n      &quot;priority&quot;: &quot;medium&quot;,\n      &quot;due_date&quot;: &quot;2026-05-06&quot;,\n      &quot;blocked&quot;: f</code> |
| `heldout_pyd_task_004` | `pydantic_adherence` | `metta_runtime` | 0 | 0 | 0 | <code>{&quot;task_label_failures&quot;: [{&quot;task&quot;: &quot;my_task&quot;, &quot;priority&quot;: &quot;medium&quot;, &quot;blocked&quot;: false, &quot;due_date&quot;: &quot;2026-05-06&quot;}]}</code> |
| `heldout_pyd_task_004` | `pydantic_adherence` | `metta_runtime_repair` | 0 | 0 | 0 | <code>{&quot;task_label_failures&quot;: [{&quot;task&quot;: &quot;my_task&quot;, &quot;priority&quot;: &quot;medium&quot;, &quot;blocked&quot;: false, &quot;due_date&quot;: &quot;2026-05-06&quot;}]}</code> |
| `heldout_pyd_task_005` | `pydantic_adherence` | `baseline` | 0 | 0 | 0 | <code>{&quot;receipts&quot;: [{&quot;priority&quot;: &quot;low&quot;, &quot;due_date&quot;: &quot;2026-05-07&quot;, &quot;blocked&quot;: false}]}</code> |
| `heldout_pyd_task_005` | `pydantic_adherence` | `pure_trm` | 1 | 1 | 1 | <code>{\n  &quot;blocked&quot;: false,\n  &quot;due_date&quot;: &quot;2026-05-07&quot;,\n  &quot;priority&quot;: &quot;low&quot;,\n  &quot;task&quot;: &quot;ship receipts&quot;\n}</code> |
| `heldout_pyd_task_005` | `pydantic_adherence` | `metta_runtime` | 1 | 1 | 1 | <code>{&quot;task&quot;: &quot;ship receipts&quot;, &quot;priority&quot;: &quot;low&quot;, &quot;due_date&quot;: &quot;2026-05-07&quot;, &quot;blocked&quot;: false}</code> |
| `heldout_pyd_task_005` | `pydantic_adherence` | `metta_runtime_repair` | 1 | 1 | 1 | <code>{&quot;task&quot;: &quot;ship receipts&quot;, &quot;priority&quot;: &quot;low&quot;, &quot;due_date&quot;: &quot;2026-05-07&quot;, &quot;blocked&quot;: false}</code> |
| `heldout_pyd_component_001` | `pydantic_adherence` | `baseline` | 0 | 0 | 0 | <code>{&quot;component&quot;:&quot;router&quot;,&quot;retries&quot;:1,&quot;safe&quot;:true}</code> |
| `heldout_pyd_component_001` | `pydantic_adherence` | `pure_trm` | 1 | 1 | 1 | <code>{&quot;name&quot;: &quot;router&quot;, &quot;retries&quot;: 1, &quot;safe&quot;: true}</code> |
| `heldout_pyd_component_001` | `pydantic_adherence` | `metta_runtime` | 1 | 1 | 1 | <code>{&quot;name&quot;: &quot;router&quot;, &quot;retries&quot;: 1, &quot;safe&quot;: true}</code> |
| `heldout_pyd_component_001` | `pydantic_adherence` | `metta_runtime_repair` | 1 | 1 | 1 | <code>{&quot;name&quot;: &quot;router&quot;, &quot;retries&quot;: 1, &quot;safe&quot;: true}</code> |
| `heldout_pyd_component_002` | `pydantic_adherence` | `baseline` | 0 | 1 | 0 | <code>{&quot;name&quot;:&quot;component_name_retriever&quot;,&quot;retries&quot;:2,&quot;safe&quot;:true}</code> |
| `heldout_pyd_component_002` | `pydantic_adherence` | `pure_trm` | 0 | 0 | 0 | <code>{&quot;component_name&quot;: &quot;component_name_retriever&quot;, &quot;retries&quot;: 2, &quot;safe&quot;: true}</code> |
| `heldout_pyd_component_002` | `pydantic_adherence` | `metta_runtime` | 0 | 1 | 0 | <code>{&quot;name&quot;: &quot;component_name_retriever&quot;, &quot;retries&quot;: 2, &quot;safe&quot;: true}</code> |
| `heldout_pyd_component_002` | `pydantic_adherence` | `metta_runtime_repair` | 0 | 1 | 0 | <code>{&quot;name&quot;: &quot;component_name_retriever&quot;, &quot;retries&quot;: 2, &quot;safe&quot;: true}</code> |
| `heldout_pyd_component_003` | `pydantic_adherence` | `baseline` | 1 | 1 | 1 | <code>{&quot;name&quot;:&quot;auditor&quot;,&quot;retries&quot;:3,&quot;safe&quot;:false}</code> |
| `heldout_pyd_component_003` | `pydantic_adherence` | `pure_trm` | 0 | 0 | 0 | <code>{&quot;component_name&quot;: &quot;auditor&quot;, &quot;retries&quot;: 3, &quot;safe&quot;: false}</code> |
| `heldout_pyd_component_003` | `pydantic_adherence` | `metta_runtime` | 1 | 1 | 1 | <code>{&quot;name&quot;: &quot;auditor&quot;, &quot;retries&quot;: 3, &quot;safe&quot;: false}</code> |
| `heldout_pyd_component_003` | `pydantic_adherence` | `metta_runtime_repair` | 1 | 1 | 1 | <code>{&quot;name&quot;: &quot;auditor&quot;, &quot;retries&quot;: 3, &quot;safe&quot;: false}</code> |
| `heldout_pyd_component_004` | `pydantic_adherence` | `baseline` | 0 | 0 | 0 | <code>{&quot;component&quot;:&quot;repairer&quot;,&quot;retries&quot;:2,&quot;safe&quot;:true}</code> |
| `heldout_pyd_component_004` | `pydantic_adherence` | `pure_trm` | 1 | 1 | 1 | <code>{&quot;name&quot;: &quot;repairer&quot;, &quot;retries&quot;: 2, &quot;safe&quot;: true}</code> |
| `heldout_pyd_component_004` | `pydantic_adherence` | `metta_runtime` | 0 | 0 | 0 | <code>{&quot;env_family&quot;: &quot;pydantic_adherence&quot;, &quot;failure_labels&quot;: [&quot;json_parse&quot;, &quot;type_error&quot;], &quot;validator&quot;: {&quot;required&quot;: {&quot;name&quot;: &quot;str&quot;, &qu</code> |
| `heldout_pyd_component_004` | `pydantic_adherence` | `metta_runtime_repair` | 0 | 0 | 0 | <code>{&quot;env_family&quot;: &quot;pydantic_adherence&quot;, &quot;failure_labels&quot;: [&quot;json_parse&quot;, &quot;type_error&quot;], &quot;validator&quot;: {&quot;required&quot;: {&quot;name&quot;: &quot;str&quot;, &qu</code> |
| `heldout_pyd_component_005` | `pydantic_adherence` | `baseline` | 0 | 0 | 0 | <code>{&quot;committer&quot;: &quot;false&quot;, &quot;retries&quot;: 1}</code> |
| `heldout_pyd_component_005` | `pydantic_adherence` | `pure_trm` | 0 | 0 | 0 | <code>{&quot;component_name&quot;: &quot;committer&quot;, &quot;retries&quot;: 1, &quot;safe&quot;: false}</code> |
| `heldout_pyd_component_005` | `pydantic_adherence` | `metta_runtime` | 0 | 0 | 0 | <code>{&quot;committer&quot;: &quot;user&quot;, &quot;retries&quot;: 1, &quot;safe&quot;: false}</code> |
| `heldout_pyd_component_005` | `pydantic_adherence` | `metta_runtime_repair` | 0 | 0 | 0 | <code>{&quot;committer&quot;: &quot;user&quot;, &quot;retries&quot;: 1, &quot;safe&quot;: false}</code> |
| `heldout_ascii_001_docs` | `ascii_tree` | `baseline` | 0 | 0 | 0 | <code>root\n \|\n \|__ drafts\n \|__ figures\n \|__ refs</code> |
| `heldout_ascii_001_docs` | `ascii_tree` | `pure_trm` | 0 | 0 | 1 | <code>```ascii\ndocs\n\|-- drafts\n\|-- figures\n`-- refs\n```</code> |
| `heldout_ascii_001_docs` | `ascii_tree` | `metta_runtime` | 1 | 1 | 1 | <code>docs\n\|-- drafts\n\|-- figures\n`-- refs</code> |
| `heldout_ascii_001_docs` | `ascii_tree` | `metta_runtime_repair` | 1 | 1 | 1 | <code>docs\n\|-- drafts\n\|-- figures\n`-- refs</code> |
| `heldout_ascii_002_eval` | `ascii_tree` | `baseline` | 0 | 0 | 0 | <code>eval\n   /  \\n holdout  results</code> |
| `heldout_ascii_002_eval` | `ascii_tree` | `pure_trm` | 0 | 0 | 1 | <code>```\nroot\n\|-- eval\n\|   \|-- rows\n\|   `-- heldout\n`-- results\n```</code> |
| `heldout_ascii_002_eval` | `ascii_tree` | `metta_runtime` | 0 | 0 | 1 | <code>```\neval\n\|-- rows\n\|   `-- heldout\n`-- results\n```</code> |
| `heldout_ascii_002_eval` | `ascii_tree` | `metta_runtime_repair` | 0 | 0 | 1 | <code>```\neval\n\|-- rows\n\|   `-- heldout\n`-- results\n```</code> |
| `heldout_ascii_003_tools` | `ascii_tree` | `baseline` | 0 | 0 | 1 | <code>root\n \\n  tools\n   \\n    search\n     \\n      weather\n       \\n        calendar</code> |
| `heldout_ascii_003_tools` | `ascii_tree` | `pure_trm` | 0 | 0 | 1 | <code>```\ntools\n\|-- search\n\|-- weather\n`-- calendar\n```</code> |
| `heldout_ascii_003_tools` | `ascii_tree` | `metta_runtime` | 0 | 0 | 1 | <code>```\ntools\n\|-- search\n\|-- weather\n`-- calendar\n```</code> |
| `heldout_ascii_003_tools` | `ascii_tree` | `metta_runtime_repair` | 0 | 0 | 1 | <code>```\ntools\n\|-- search\n\|-- weather\n`-- calendar\n```</code> |
| `heldout_ascii_004_gate` | `ascii_tree` | `baseline` | 0 | 0 | 1 | <code>root\n  / \| \\n gate parse validate commit</code> |
| `heldout_ascii_004_gate` | `ascii_tree` | `pure_trm` | 0 | 0 | 1 | <code>root  \n\|-- gate  \n\|-- parse  \n\|-- validate  \n\|-- commit</code> |
| `heldout_ascii_004_gate` | `ascii_tree` | `metta_runtime` | 1 | 1 | 1 | <code>gate\n\|-- parse\n\|-- validate\n`-- commit</code> |
| `heldout_ascii_004_gate` | `ascii_tree` | `metta_runtime_repair` | 1 | 1 | 1 | <code>gate\n\|-- parse\n\|-- validate\n`-- commit</code> |
| `heldout_ascii_005_pipe` | `ascii_tree` | `baseline` | 0 | 0 | 1 | <code>```\n      root\n     /  \\n   pipeline  collect\n       /  \\n     score  audit\n```</code> |
| `heldout_ascii_005_pipe` | `ascii_tree` | `pure_trm` | 0 | 0 | 1 | <code>```plaintext\npipeline\n\|-- collect\n\|-- score\n`-- audit\n```</code> |
| `heldout_ascii_005_pipe` | `ascii_tree` | `metta_runtime` | 0 | 0 | 1 | <code>pipeline\n\|-- collect\n\|-- score\n`-- audit</code> |
| `heldout_ascii_005_pipe` | `ascii_tree` | `metta_runtime_repair` | 1 | 1 | 1 | <code>pipeline\n\|-- collect\n\|   `-- score\n`-- audit</code> |
| `heldout_ascii_006_repo` | `ascii_tree` | `baseline` | 0 | 0 | 0 | <code>skills\n  \_ studies\n    \_ scripts</code> |
| `heldout_ascii_006_repo` | `ascii_tree` | `pure_trm` | 0 | 0 | 1 | <code>\|--- repo\n\|   \|-- skills\n\|   \|-- studies\n\|   `-- scripts</code> |
| `heldout_ascii_006_repo` | `ascii_tree` | `metta_runtime` | 1 | 1 | 1 | <code>repo\n\|-- skills\n\|-- studies\n`-- scripts</code> |
| `heldout_ascii_006_repo` | `ascii_tree` | `metta_runtime_repair` | 1 | 1 | 1 | <code>repo\n\|-- skills\n\|-- studies\n`-- scripts</code> |
| `heldout_ascii_007_agent` | `ascii_tree` | `baseline` | 0 | 0 | 0 | <code>root\n  /  \\nroute  project\n      \\n       report</code> |
| `heldout_ascii_007_agent` | `ascii_tree` | `pure_trm` | 0 | 0 | 1 | <code>```plaintext\nagent\n\|-- route\n\|   `-- project\n`-- report\n```</code> |
| `heldout_ascii_007_agent` | `ascii_tree` | `metta_runtime` | 0 | 0 | 1 | <code>agent\n\|-- route\n   `-- project\n`-- report</code> |
| `heldout_ascii_007_agent` | `ascii_tree` | `metta_runtime_repair` | 0 | 0 | 1 | <code>agent\n\|-- route\n   `-- project\n`-- report</code> |
| `heldout_ascii_008_model` | `ascii_tree` | `baseline` | 0 | 0 | 0 | <code>o\n   / \\n  o   o\n / \ / \\no   o o   o</code> |
| `heldout_ascii_008_model` | `ascii_tree` | `pure_trm` | 0 | 0 | 1 | <code>```plaintext\nmodel\n\|-- prompt\n\|-- output\n`-- verdict\n```</code> |
| `heldout_ascii_008_model` | `ascii_tree` | `metta_runtime` | 0 | 0 | 1 | <code>```\nmodel\n\|-- prompt\n\|-- output\n`-- verdict\n```</code> |
| `heldout_ascii_008_model` | `ascii_tree` | `metta_runtime_repair` | 0 | 0 | 1 | <code>```\nmodel\n\|-- prompt\n\|-- output\n\|-- root model\n`-- verdict\n```</code> |
| `heldout_bullets_001` | `ifeval_contract_family` | `baseline` | 1 | 1 | 1 | <code>- parse\n- validate\n- commit</code> |
| `heldout_bullets_001` | `ifeval_contract_family` | `pure_trm` | 1 | 1 | 1 | <code>- Parse the contract.\n- Validate the contract.\n- Commit the contract.</code> |
| `heldout_bullets_001` | `ifeval_contract_family` | `metta_runtime` | 0 | 1 | 0 | <code>- line_count: 1\n- extra_text: 2\n- validator: 3</code> |
| `heldout_bullets_001` | `ifeval_contract_family` | `metta_runtime_repair` | 0 | 1 | 0 | <code>- line_count: 1\n- extra_text: 2\n- validator: 3</code> |
| `heldout_bullets_002` | `ifeval_contract_family` | `baseline` | 1 | 1 | 1 | <code>- collect rows: gather data from various sources\n- score rows: evaluate data based on predefined criteria\n- audit claims: verify accuracy and completeness of collected data</code> |
| `heldout_bullets_002` | `ifeval_contract_family` | `pure_trm` | 1 | 1 | 1 | <code>- Collect rows: 123\n- Score rows: 456\n- Audit claims: 789</code> |
| `heldout_bullets_002` | `ifeval_contract_family` | `metta_runtime` | 1 | 1 | 1 | <code>- Collect rows\n- Score rows\n- Audit claims</code> |
| `heldout_bullets_002` | `ifeval_contract_family` | `metta_runtime_repair` | 1 | 1 | 1 | <code>- Collect rows\n- Score rows\n- Audit claims</code> |
| `heldout_bullets_003` | `ifeval_contract_family` | `baseline` | 1 | 1 | 1 | <code>- freeze prompts\n- run models\n- compare arms</code> |
| `heldout_bullets_003` | `ifeval_contract_family` | `pure_trm` | 1 | 1 | 1 | <code>- Freeze prompts to ensure consistency and prevent unintended changes.\n- Run models to validate the outcomes and ensure accuracy.\n- Compare arms to identify and mitigate any discrepancies or vulnerabilities.</code> |
| `heldout_bullets_003` | `ifeval_contract_family` | `metta_runtime` | 1 | 1 | 1 | <code>- Freeze prompts\n- Run models\n- Compare arms</code> |
| `heldout_bullets_003` | `ifeval_contract_family` | `metta_runtime_repair` | 1 | 1 | 1 | <code>- Freeze prompts\n- Run models\n- Compare arms</code> |
| `heldout_bullets_004` | `ifeval_contract_family` | `baseline` | 1 | 1 | 1 | <code>- label failures: &quot;failed to load&quot;, &quot;invalid input&quot;, &quot;file not found&quot;\n- repair outputs: &quot;reloading data&quot;, &quot;resetting settings&quot;, &quot;restarting service&quot;\n- log rec</code> |
| `heldout_bullets_004` | `ifeval_contract_family` | `pure_trm` | 0 | 1 | 0 | <code>- line_count failure\n- extra_text failure\n- log_receipts failure</code> |
| `heldout_bullets_004` | `ifeval_contract_family` | `metta_runtime` | 1 | 1 | 1 | <code>- label failures: line_count, extra_text\n- repair outputs: \n- log receipts:</code> |
| `heldout_bullets_004` | `ifeval_contract_family` | `metta_runtime_repair` | 1 | 1 | 1 | <code>- label failures: line_count, extra_text\n- repair outputs: \n- log receipts:</code> |
| `heldout_bullets_005` | `ifeval_contract_family` | `baseline` | 1 | 1 | 1 | <code>- route tools show\n- fill args with\n- check schema against</code> |
| `heldout_bullets_005` | `ifeval_contract_family` | `pure_trm` | 1 | 1 | 1 | <code>- route tools\n- fill args\n- check schema</code> |
| `heldout_bullets_005` | `ifeval_contract_family` | `metta_runtime` | 1 | 1 | 1 | <code>- route tools\n- fill args\n- check schema</code> |
| `heldout_bullets_005` | `ifeval_contract_family` | `metta_runtime_repair` | 1 | 1 | 1 | <code>- route tools\n- fill args\n- check schema</code> |
| `heldout_bullets_006` | `ifeval_contract_family` | `baseline` | 1 | 1 | 1 | <code>- draft table\n- render figure\n- write claim</code> |
| `heldout_bullets_006` | `ifeval_contract_family` | `pure_trm` | 1 | 1 | 1 | <code>- Draft the table using the provided template.\n- Render the figure according to the specified guidelines.\n- Write the claim based on the given data.</code> |
| `heldout_bullets_006` | `ifeval_contract_family` | `metta_runtime` | 1 | 1 | 1 | <code>- Draft table completed\n- Figure rendered successfully\n- Claim written and validated</code> |
| `heldout_bullets_006` | `ifeval_contract_family` | `metta_runtime_repair` | 1 | 1 | 1 | <code>- Draft table completed\n- Figure rendered successfully\n- Claim written and validated</code> |
| `heldout_bullets_007` | `ifeval_contract_family` | `baseline` | 1 | 1 | 1 | <code>- Load rows\n- Call model\n- Store verdicts</code> |
| `heldout_bullets_007` | `ifeval_contract_family` | `pure_trm` | 1 | 1 | 1 | <code>- Load rows.\n- Call model.\n- Store verdicts.</code> |
| `heldout_bullets_007` | `ifeval_contract_family` | `metta_runtime` | 1 | 1 | 1 | <code>- Load rows\n- Call model\n- Store verdicts</code> |
| `heldout_bullets_007` | `ifeval_contract_family` | `metta_runtime_repair` | 1 | 1 | 1 | <code>- Load rows\n- Call model\n- Store verdicts</code> |
| `heldout_bullets_008` | `ifeval_contract_family` | `baseline` | 1 | 1 | 1 | <code>- reject leak\n- guard split\n- publish audit</code> |
| `heldout_bullets_008` | `ifeval_contract_family` | `pure_trm` | 1 | 1 | 1 | <code>- reject leak\n- guard split\n- publish audit</code> |
| `heldout_bullets_008` | `ifeval_contract_family` | `metta_runtime` | 1 | 1 | 1 | <code>- reject leak\n- guard split\n- publish audit</code> |
| `heldout_bullets_008` | `ifeval_contract_family` | `metta_runtime_repair` | 1 | 1 | 1 | <code>- reject leak\n- guard split\n- publish audit</code> |
| `heldout_array_001` | `ifeval_contract_family` | `baseline` | 1 | 1 | 1 | <code>[&quot;route&quot;, &quot;repair&quot;, &quot;commit&quot;]</code> |
| `heldout_array_001` | `ifeval_contract_family` | `pure_trm` | 1 | 1 | 1 | <code>[&quot;route&quot;, &quot;repair&quot;, &quot;commit&quot;]</code> |
| `heldout_array_001` | `ifeval_contract_family` | `metta_runtime` | 1 | 1 | 1 | <code>[&quot;route&quot;, &quot;repair&quot;, &quot;commit&quot;]</code> |
| `heldout_array_001` | `ifeval_contract_family` | `metta_runtime_repair` | 1 | 1 | 1 | <code>[&quot;route&quot;, &quot;repair&quot;, &quot;commit&quot;]</code> |
| `heldout_array_002` | `ifeval_contract_family` | `baseline` | 1 | 1 | 1 | <code>[&quot;train&quot;, &quot;validate&quot;, &quot;holdout&quot;]</code> |
| `heldout_array_002` | `ifeval_contract_family` | `pure_trm` | 1 | 1 | 1 | <code>[&quot;train&quot;, &quot;validate&quot;, &quot;holdout&quot;]</code> |
| `heldout_array_002` | `ifeval_contract_family` | `metta_runtime` | 1 | 1 | 1 | <code>[&quot;train&quot;, &quot;validate&quot;, &quot;holdout&quot;]</code> |
| `heldout_array_002` | `ifeval_contract_family` | `metta_runtime_repair` | 1 | 1 | 1 | <code>[&quot;train&quot;, &quot;validate&quot;, &quot;holdout&quot;]</code> |
| `heldout_array_003` | `ifeval_contract_family` | `baseline` | 1 | 1 | 1 | <code>[&quot;search&quot;, &quot;read&quot;, &quot;answer&quot;]</code> |
| `heldout_array_003` | `ifeval_contract_family` | `pure_trm` | 1 | 1 | 1 | <code>[&quot;search&quot;, &quot;read&quot;, &quot;answer&quot;]</code> |
| `heldout_array_003` | `ifeval_contract_family` | `metta_runtime` | 1 | 1 | 1 | <code>[&quot;search&quot;, &quot;read&quot;, &quot;answer&quot;]</code> |
| `heldout_array_003` | `ifeval_contract_family` | `metta_runtime_repair` | 1 | 1 | 1 | <code>[&quot;search&quot;, &quot;read&quot;, &quot;answer&quot;]</code> |
| `heldout_array_004` | `ifeval_contract_family` | `baseline` | 1 | 1 | 1 | <code>[&quot;schema&quot;, &quot;args&quot;, &quot;call&quot;]</code> |
| `heldout_array_004` | `ifeval_contract_family` | `pure_trm` | 1 | 1 | 1 | <code>[&quot;schema&quot;, &quot;args&quot;, &quot;call&quot;]</code> |
| `heldout_array_004` | `ifeval_contract_family` | `metta_runtime` | 1 | 1 | 1 | <code>[&quot;schema&quot;, &quot;args&quot;, &quot;call&quot;]</code> |
| `heldout_array_004` | `ifeval_contract_family` | `metta_runtime_repair` | 1 | 1 | 1 | <code>[&quot;schema&quot;, &quot;args&quot;, &quot;call&quot;]</code> |
| `heldout_array_005` | `ifeval_contract_family` | `baseline` | 1 | 1 | 1 | <code>[&quot;draft&quot;, &quot;score&quot;, &quot;audit&quot;]</code> |
| `heldout_array_005` | `ifeval_contract_family` | `pure_trm` | 1 | 1 | 1 | <code>[&quot;draft&quot;, &quot;score&quot;, &quot;audit&quot;]</code> |
| `heldout_array_005` | `ifeval_contract_family` | `metta_runtime` | 1 | 1 | 1 | <code>[&quot;draft&quot;, &quot;score&quot;, &quot;audit&quot;]</code> |
| `heldout_array_005` | `ifeval_contract_family` | `metta_runtime_repair` | 1 | 1 | 1 | <code>[&quot;draft&quot;, &quot;score&quot;, &quot;audit&quot;]</code> |
| `heldout_array_006` | `ifeval_contract_family` | `baseline` | 1 | 1 | 1 | <code>[&quot;rows&quot;, &quot;metrics&quot;, &quot;claims&quot;]</code> |
| `heldout_array_006` | `ifeval_contract_family` | `pure_trm` | 1 | 1 | 1 | <code>[&quot;rows&quot;, &quot;metrics&quot;, &quot;claims&quot;]</code> |
| `heldout_array_006` | `ifeval_contract_family` | `metta_runtime` | 1 | 1 | 1 | <code>[&quot;rows&quot;, &quot;metrics&quot;, &quot;claims&quot;]</code> |
| `heldout_array_006` | `ifeval_contract_family` | `metta_runtime_repair` | 1 | 1 | 1 | <code>[&quot;rows&quot;, &quot;metrics&quot;, &quot;claims&quot;]</code> |
| `heldout_bool_001` | `boolq_choice_contract` | `baseline` | 0 | 0 | 0 | <code>Yes</code> |
| `heldout_bool_001` | `boolq_choice_contract` | `pure_trm` | 1 | 1 | 1 | <code>true</code> |
| `heldout_bool_001` | `boolq_choice_contract` | `metta_runtime` | 1 | 1 | 1 | <code>true</code> |
| `heldout_bool_001` | `boolq_choice_contract` | `metta_runtime_repair` | 1 | 1 | 1 | <code>true</code> |
| `heldout_bool_002` | `boolq_choice_contract` | `baseline` | 0 | 0 | 0 | <code>No</code> |
| `heldout_bool_002` | `boolq_choice_contract` | `pure_trm` | 1 | 1 | 1 | <code>false</code> |
| `heldout_bool_002` | `boolq_choice_contract` | `metta_runtime` | 1 | 1 | 1 | <code>false</code> |
| `heldout_bool_002` | `boolq_choice_contract` | `metta_runtime_repair` | 1 | 1 | 1 | <code>false</code> |
| `heldout_bool_003` | `boolq_choice_contract` | `baseline` | 0 | 0 | 0 | <code>Yes</code> |
| `heldout_bool_003` | `boolq_choice_contract` | `pure_trm` | 1 | 1 | 1 | <code>true</code> |
| `heldout_bool_003` | `boolq_choice_contract` | `metta_runtime` | 1 | 1 | 1 | <code>true</code> |
| `heldout_bool_003` | `boolq_choice_contract` | `metta_runtime_repair` | 1 | 1 | 1 | <code>true</code> |
| `heldout_choice_004` | `choice_contract` | `baseline` | 1 | 1 | 1 | <code>B</code> |
| `heldout_choice_004` | `choice_contract` | `pure_trm` | 1 | 1 | 1 | <code>B</code> |
| `heldout_choice_004` | `choice_contract` | `metta_runtime` | 1 | 1 | 1 | <code>B</code> |
| `heldout_choice_004` | `choice_contract` | `metta_runtime_repair` | 1 | 1 | 1 | <code>B</code> |
| `heldout_choice_005` | `choice_contract` | `baseline` | 1 | 1 | 1 | <code>B</code> |
| `heldout_choice_005` | `choice_contract` | `pure_trm` | 0 | 1 | 0 | <code>C</code> |
| `heldout_choice_005` | `choice_contract` | `metta_runtime` | 1 | 1 | 1 | <code>B</code> |
| `heldout_choice_005` | `choice_contract` | `metta_runtime_repair` | 1 | 1 | 1 | <code>B</code> |
| `heldout_pipe_001` | `structured_contract` | `baseline` | 1 | 1 | 1 | <code>2026-05-08\|eval\|ready</code> |
| `heldout_pipe_001` | `structured_contract` | `pure_trm` | 0 | 0 | 0 | <code>date\|owner\|status\n2026-05-08\|eval\|ready</code> |
| `heldout_pipe_001` | `structured_contract` | `metta_runtime` | 1 | 1 | 1 | <code>2026-05-08\|eval\|ready</code> |
| `heldout_pipe_001` | `structured_contract` | `metta_runtime_repair` | 1 | 1 | 1 | <code>2026-05-08\|eval\|ready</code> |
| `heldout_pipe_002` | `structured_contract` | `baseline` | 1 | 1 | 1 | <code>2026-05-09\|audit\|blocked</code> |
| `heldout_pipe_002` | `structured_contract` | `pure_trm` | 0 | 0 | 0 | <code>date\|owner\|status\n2026-05-09\|audit\|blocked</code> |
| `heldout_pipe_002` | `structured_contract` | `metta_runtime` | 1 | 1 | 1 | <code>2026-05-09\|audit\|blocked</code> |
| `heldout_pipe_002` | `structured_contract` | `metta_runtime_repair` | 1 | 1 | 1 | <code>2026-05-09\|audit\|blocked</code> |
| `heldout_pipe_003` | `structured_contract` | `baseline` | 1 | 1 | 1 | <code>2026-05-10\|paper\|ready</code> |
| `heldout_pipe_003` | `structured_contract` | `pure_trm` | 0 | 0 | 0 | <code>date\|owner\|status\n2026-05-10\|paper\|ready</code> |
| `heldout_pipe_003` | `structured_contract` | `metta_runtime` | 1 | 1 | 1 | <code>2026-05-10\|paper\|ready</code> |
| `heldout_pipe_003` | `structured_contract` | `metta_runtime_repair` | 1 | 1 | 1 | <code>2026-05-10\|paper\|ready</code> |

## Claim Audit

- Allowed: this is a live local 3B result against frozen validators.
- Not allowed: do not call this trained TRM lift; interpret benchmark status according to the study claim audit and row-suite scope.
- Not allowed: do not call `metta_runtime_repair` learned TRM lift; it is a repair-prompt arm using the same 3B model plus public validator feedback.
