"""
author: Yichen Zhang
"""
import pandas as pd
import numpy as np
from Voting import Voting

class ApprovalVoting(Voting):
    
    class ApprovalBallot(Voting.Ballot):
        
        def __init__(self, scores):
            super().__init__(scores)
            
        def isValid(self, try_handle_invalid=True):
            if try_handle_invalid:
                # fill missing values with 0
                self.scores.fillna(0, inplace=True)
            # check if there is any missing value
            if self.scores.isna().any():
                return False
            # check if self.scores is numeric
            if not np.issubdtype(self.scores.dtype, np.number):
                return False
            # interpret the largest score as approval, if specified to
            # all 0 (no approval) will not be parsed into all 1 (approve all)
            if try_handle_invalid and not (self.scores==0).all():
                self.scores = (self.scores==self.scores.max()).astype(int)
            # check whether the ballot only votes 0 or 1 for each candidate
            return self.scores.isin([0, 1]).all()
        
        def Vote(self, candidates):
            # vote 0 or 1 for candidates, can be all 0 or all 1
            return self.scores.loc[candidates]
        
        def Export(self, candidates):
            return self.Vote(candidates)
    
    def __init__(self, candidates, try_handle_invalid=True):
        super().__init__(candidates, try_handle_invalid)
    
    def AddBallot(self, new_ballot):
        # support a string, a list of strings, or a Series to represent a vote
        if type(new_ballot)==str:
            ballot = self.ApprovalBallot(
                pd.Series([1 if c==new_ballot else 0 for c in self.candidates], 
                          index = self.candidates))
        elif type(new_ballot)==list:
            ballot = self.ApprovalBallot(
                pd.Series([1 if c in new_ballot else 0 
                           for c in self.candidates], 
                          index = self.candidates))
        else:
            # if some candidates have no score, fill them with 0
            new_ballot = new_ballot.copy()
            for c in self.candidates:
                if c not in new_ballot:
                    new_ballot[c] = 0
            ballot = self.ApprovalBallot(new_ballot)
        try:
            if ballot.isValid(self.try_handle_invalid):
                self.ballots.append(ballot)
                return True
            return False
        except:
            return False
    
    def ImportBallots(self, filename):
        return super().ImportBallots(filename)
        
    def ExportBallots(self, filename):
        return super().ExportBallots(filename)
    
    def RunElection(self, candidates=None):
        return super().RunElection(candidates)
    
    def SplitSize(self, num_candidates):
        return super().SplitSize(num_candidates)
    