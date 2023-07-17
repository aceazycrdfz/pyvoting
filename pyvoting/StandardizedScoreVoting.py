"""
author: Yichen Zhang
"""
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from Voting import Voting

class StandardizedScoreVoting(Voting):
    
    class StandardizedScoreBallot(Voting.Ballot):
        
        def __init__(self, scores):
            super().__init__(scores)
            
        def isValid(self, try_handle_invalid=True, score_range=(0, 5), 
                    only_int=True):
            if try_handle_invalid:
                # fill missing values with 0
                self.scores.fillna(0, inplace=True)
            # check if there is any missing value
            if self.scores.isna().any():
                return False
            # check if self.scores is numeric
            if not np.issubdtype(self.scores.dtype, np.number):
                return False
            # put out-of-bound scores into the valid range, if specified to
            if try_handle_invalid:
                self.scores.loc[self.scores>score_range[1]] = score_range[1]
                self.scores.loc[self.scores<score_range[0]] = score_range[0]
                # round non-integers, if necessary
                if only_int:
                    self.scores = self.scores.round(0)
            # check whether the ballot satisfy the constraints
            return (self.scores.between(score_range[0], score_range[1]).all() 
                    and (not only_int or self.scores.astype("float").apply(
                    lambda x: x.is_integer()).all()))
        
        def Vote(self, candidates):
            # if the score is the same for all candidates, vote 0 for all
            if self.scores.loc[candidates].nunique() == 1:
                return pd.Series(0, index=candidates)
            # normalize the scores for the candidates between -1 and 1
            return pd.Series(StandardScaler().fit_transform(self.scores.
                   loc[candidates].values.reshape(-1, 1)).flatten(), 
                   index=candidates)
        
        def Export(self, candidates):
            return self.Vote(candidates)
    
    def __init__(self, candidates, try_handle_invalid=True, score_range=(0, 5), 
                 only_int=True):
        super().__init__(candidates, try_handle_invalid)
        """
        New Parameters
        score_range : tuple, default=(0, 5)
            an integer tuple representing the lower bound and the upper bound 
            of the scores, both inclusive
        only_int : bool, default=True
            whether only integer scores is allowed
        """
        self.score_range = score_range
        self.only_int = only_int
    
    def AddBallot(self, new_ballot):
        new_ballot = new_ballot.copy()
        if self.try_handle_invalid:
            # if some candidates have no score, fill the scores with 0
            default_score = 0
        else:
            # if some candidates have no score, fill the scores with NaN
            default_score = np.nan
        for c in self.candidates:
            if c not in new_ballot:
                new_ballot[c] = default_score
        ballot = self.StandardizedScoreBallot(new_ballot)
        try:
            if ballot.isValid(self.try_handle_invalid, self.score_range, 
                              self.only_int):
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
    