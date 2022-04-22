# Secret Hitler Prediction Algorithm

## Model
### Variables
The probabilities in the model tables depend on some variables. These are named according to the format `[FILE]_[SCENARIO]_[DESCRIPTION]`.
- `[FILE]` identifies the table in which the variable is used.
	- `CC` is `claim_chan` (which models the chancellor's description of the legislative session).
	- `CP` is `claim_pres` (which models the president's description of the legislative session).
	- `PC` is `policy_chan` (which models the chancellor's policy decision).
	- `PP` is `policy_pres` (which models the president's policy decision).
- `[SCENARIO]` identifies the situation in which the player finds themself (i.e. the givens). The format varies by table.
	- For `claim_chan`, the format is `[CHAN][ACTUAL][CLAIM][OUTCOME]`. `[CHAN]` is the first letter of the chancellor's role. `[ACTUAL]` is the number of liberal policies received by chancellor and `[CLAIM]` is the number of liberal policies that the pesident claims to have given. `[OUTCOME]` is the first letter of the legislative session outcome (i.e. `F` for fascist or `L` for liberal).
	- For `claim_pres`, the format is `[PRES][CHAN][OUTCOME]`. `[PRES]` and `[CHAN]` are the first letters of the roles of the president and chancellor, respectively. `[OUTCOME]` is the first letter of the legislative session outcome.
	- For `policy_chan`, the format is `[PRES][CHAN]`, where `[PRES]` and `[CHAN]` are the first letters of the roles of the president and chancellor, respectively.
	- For `policy_pres`, the format is `[PRES][CHAN][N]`. `[PRES]` and `[CHAN]` are the first letters of the roles of the president and chancellor, respectively. `[N]` is the number of liberal policies in the three policies that the president picked up.
	- _NOTE:_ In cases where the role of the president or chancellor is unimportant, the letter `X` is used. For example, liberal players typically do not know who is who and should therefore act the same regardless of their partner's role.
- `[DESCRIPTION]` is a short description of the player's response.
