# Secret Hitler Prediction Algorithm

## Model
### Variables
The probabilities in the model tables depend on some variables. These are named according to the format `[FILE]_[SCENARIO]_[DESCRIPTION]`.
- `[FILE]` identifies the table in which the variable is used.
	- `CC` is `claim_chan` (which models the Chancellor's description of the legislative session).
	- `CP` is `claim_pres` (which models the President's description of the legislative session).
	- `PC` is `policy_chan` (which models the Chancellor's policy decision).
	- `PP` is `policy_pres` (which models the President's policy decision).
	- `INV` is `inv_target` (which models the President's choice of target for an investigation)
- `[SCENARIO]` identifies the situation in which the player finds themself (i.e. the givens). The format varies by table.
	- For `claim_chan`, the format is `[CHAN][ACTUAL][CLAIM][OUTCOME]`. `[CHAN]` is the first letter of the Chancellor's role. `[ACTUAL]` is the number of Liberal policies received by Chancellor and `[CLAIM]` is the number of Liberal policies that the pesident claims to have given. `[OUTCOME]` is the first letter of the legislative session outcome (i.e. `F` for Fascist or `L` for Liberal).
	- For `claim_pres`, the format is `[PRES][CHAN][OUTCOME]`. `[PRES]` and `[CHAN]` are the first letters of the roles of the President and Chancellor, respectively. `[OUTCOME]` is the first letter of the legislative session outcome.
	- For `policy_chan`, the format is `[PRES][CHAN]`, where `[PRES]` and `[CHAN]` are the first letters of the roles of the President and Chancellor, respectively.
	- For `policy_pres`, the format is `[PRES][CHAN][N]`. `[PRES]` and `[CHAN]` are the first letters of the roles of the President and Chancellor, respectively. `[N]` is the number of Liberal policies in the three policies that the President picked up.
	- For `inv_target`, the description is the first letter of the President's role.
	- _NOTE:_ In cases where the role of the President or Chancellor is unimportant, the letter `X` is used. For example, Liberal players typically do not know who is who and should therefore act the same regardless of their partner's role.
- `[DESCRIPTION]` is a short description of the player's response.
