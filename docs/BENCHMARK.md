# Benchmark definition

WISP evaluates an observable solve-and-edit interface. Models receive a worksheet and the task information available in the selected condition, and return an edited image on the same canvas. Correct output requires the requested answer, correct destination and edit count, preservation of unrelated content, and the task's format requirements.

## Core tasks

| Family | Paper task | Stable implementation ID |
|---|---|---|
| Marking | Line-Intersection Marking | `line_intersections` |
| Marking | Line-Midpoint Marking | `line_midpoint_mark` |
| Marking | Dot-Circling Marking | `count_dots_visual` |
| Marking | Overlapping-Shape Center Marking | `overlapping_shapes` |
| Filling | Target-Shape Filling | `fill_target_shape` |
| Copying | Circled-Letter Copying | `circled_letter_base` |
| Copying | Identical-Letter Copying (All-A Control) | `circled_letter_allA` |
| Copying | Single-Letter Copying | `circled_letter_copy_single` |
| Counting | Dot Counting to Digit | `count_dots_digit` |
| Suppression | Blank-Answer Suppression | `circled_letter_blank` |
| Suppression | Empty-Circle Suppression | `circled_letter_blankcircle` |

Active tasks require red answer edits. Suppression controls require **no answer edit**. Existing black geometry, printed instructions, answer boxes, and frame should be preserved.

## Information conditions

| ID | Label | Task-specific external prompt | In-image instruction | References |
|---|---|:--:|:--:|:--:|
| V0 | PRM | Yes | No | No |
| V1 | PRM+TXT | Yes | Yes | No |
| V2 | TXT | No | Yes | No |
| V3 | MIN | No | No | No |
| V4 | PRM+REF | Yes | No | Two |
| V5 | PRM+TXT+REF | Yes | Yes | Two |
| V6 | MIN+REF | No | No | Two |
| V7 | TXT+REF | No | Yes | Two |

TXT conditions use a generic external direction to follow the written instructions in the image. MIN and MIN+REF use `Edit the image.` Each REF item provides one style reference and one input–output demonstration. Exact prompt-condition definitions are in [the configuration](../configs/model_prompts_v0_v7.yaml); generated item records contain the complete external prompt.

PRM/TXT conditions measure instruction-conditioned problem solving. MIN/MIN+REF are more induction-oriented, but success does not establish transfer to unseen rule families, layouts, or symbols. The worksheet templates and fixed layout are deliberate controls, not a natural-document distribution.
