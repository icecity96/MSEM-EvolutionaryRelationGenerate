# EventMapping

This project is used to generate evolutionary relationship in *stakeholder layer* and *service & feature layer*.

## Data Format
### Event Sample
| Field | Description |
| ----- | ----- |
| text | News Title |
| time | when the event is published |
| labels | event components sequence (<a:int, b:int, component> sorted by `a`) |
| relation | events relation in the text |

### Rules
| Field | Description |
| -------- | -------- |
| level | If multiple rules are satisfied, choose the one with the highest `level` |
| Twords | trigger words (see `operations.py` for details) |
| Pattern | event component sequence |
| Edge | evolutionary edges should be generated |
| Required | Additional conditions |
| Return | returned components after processing (only for **Preprocess Rules**) |
