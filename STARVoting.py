"""
author: Yichen Zhang
"""
import pandas as pd
import numpy as np
from Voting import Voting

class STARVoting(Voting):
    
    class STARBallot(Voting.Ballot):
        
        def __init__(self, scores):
            super().__init__(scores)
            
        def isValid(self, try_handle_invalid=True, score_range=(0, 5), 
                    only_int=True):
            # fill missing values with 0
            self.scores.fillna(0, inplace=True)
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
        
        def Vote(self, candidates, runoff=False):
            # if runoff is set to True, will vote 1 for most prefered 
            # candidate(s) and 0 for everyone else
            if runoff:
                # if all candidates tied, vote all 0
                if self.scores.loc[candidates].nunique()==1:
                    return pd.Series(0, index=candidates)
                return pd.Series([1 if c==self.scores.loc[candidates].idxmax() 
                                  else 0 for c in candidates], 
                                 index=candidates)
            # otherwise vote the score corresponding to each candidate
            return self.scores.loc[candidates]
        
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
        # if some candidates have no score, fill them with 0
        if self.try_handle_invalid:
            new_ballot = new_ballot.copy()
            for c in self.candidates:
                if c not in new_ballot:
                    new_ballot[c] = 0
        ballot = self.STARBallot(new_ballot)
        try:
            if ballot.isValid(self.try_handle_invalid, self.score_range, 
                              self.only_int):
                self.ballots.append(ballot)
                return True
            return False
        except:
            print(new_ballot)
            return False
    
    def ImportBallots(self, filename):
        return super().ImportBallots(filename)
        
    def ExportBallots(self, filename):
        return super().ExportBallots(filename)
    
    def RunElection(self, candidates=None):
        """
        This STAR voting implementation uses a different tie-breaking protocal 
        that makes more sense and is easier to implement than the typical STAR 
        voting tie-breaking methods!
        
        The log in the returned list has a different format: a numeric tuple 
        (s1, s2) where s1 is the scoring round score and s2 is the runoff 
        round score. Those who did not make it to runoff has a runoff score 0. 
        """
        if candidates==None:
            candidates=self.candidates
        if candidates==[]:
            return []
        # add up scores from all ballots
        scores = pd.Series(data=0, index=candidates)
        for b in self.ballots:
            scores += b.Vote(candidates, runoff=False)
        # candidates with top 2 greatest scores (possibly tied) enters runoff
        upper_bracket = [c for c in candidates if (scores>scores[c]).sum()<2]
        lower_bracket = [c for c in candidates if c not in upper_bracket]
        # do runoff on upper_bracket
        scores_rf = pd.Series(data=0, index=candidates)
        for b in self.ballots:
            scores_rf += b.Vote(upper_bracket, runoff=True)
        # treat those who did not enter runoff as having 0 runoff score
        scores_rf.loc[lower_bracket] = 0
        # combine scores from two rounds and sort them
        scores_final = pd.Series([(scores_rf[c], scores[c]) for c in
                                  candidates], index=candidates)
        scores_final.sort_values(ascending=False, inplace=True)
        return [(c, (scores_final>scores_final[c]).sum()+1, 
                 (scores_final[c][1], scores_final[c][0])) 
                for c in scores_final.index]
    
    def SplitSize(self, num_candidates):
        return super().SplitSize(num_candidates)
    