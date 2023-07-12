"""
author: Yichen Zhang
"""
import pandas as pd
from PluralityVoting import PluralityVoting
from ApprovalVoting import ApprovalVoting
from ScoreVoting import ScoreVoting
from STARVoting import STARVoting
from RankedChoiceVoting import RankedChoiceVoting
from TierListVoting import TierListVoting
from TieredPopularityVoting import TieredPopularityVoting

if __name__ == "__main__":
    
    candidates = ["Trump","Pence","Biden"]
    election = TieredPopularityVoting(candidates, try_handle_invalid=True, 
                                      reverse=False, allowed_tier=0)
    #print(election.ImportBallots("ballot.xlsx"))
    
    print(election.AddBallot(pd.Series({"Trump":1,
                                        "Pence":2,
                                        "Biden":2})))
    print(election.AddBallot(pd.Series({"Trump":1,
                                        "Pence":1,
                                        "Biden":2})))
    print(election.AddBallot(pd.Series({"Trump":1,
                                        "Pence":1,
                                        "Biden":1})))
    
    print(election.RunElection())
    print(election.ExportBallots("ballot.xlsx"))
    