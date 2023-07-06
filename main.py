"""
author: Yichen Zhang
"""
import pandas as pd
from PluralityVoting import PluralityVoting
from ApprovalVoting import ApprovalVoting
from ScoreVoting import ScoreVoting
from STARVoting import STARVoting

if __name__ == "__main__":
    
    candidates = ["Trump","Pence","Biden","Clinton"]
    election = STARVoting(candidates, try_handle_invalid=True, 
                           score_range=(0, 5), only_int=False)
    #print(election.ImportBallots("ballot.xlsx"))
    
    print(election.AddBallot(pd.Series({"Trump":5,
                                        "Pence":1,
                                        "Biden":3,
                                        "Clinton":0})))
    
    print(election.AddBallot(pd.Series({"Trump":1,
                                        "Pence":2,
                                        "Biden":3,
                                        "Clinton":4})))
    
    print(election.AddBallot(pd.Series({"Trump":1,
                                        "Pence":2,
                                        "Biden":3,
                                        "Clinton":4})))
    
    print(election.RunElection(["Trump", "Pence"]))
    print(election.ExportBallots("ballot.xlsx"))
    