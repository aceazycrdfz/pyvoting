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
from NormalizedScoreVoting import NormalizedScoreVoting

if __name__ == "__main__":
    
    candidates = ["Trump","Pence","Biden"]
    election = NormalizedScoreVoting(candidates, try_handle_invalid=True)
    #print(election.ImportBallots("ballot.xlsx"))
    
    print(election.AddBallot(pd.Series({"Trump":1,
                                        "Pence":4,
                                        "Biden":5})))
    
    print(election.RunElection())
    print(election.ExportBallots("ballot.xlsx"))
    