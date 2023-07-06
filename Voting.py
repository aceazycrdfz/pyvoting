"""
author: Yichen Zhang
"""
from abc import ABC
import pandas as pd

class Voting(ABC):
    """
    Abstract Voting Class
    Represents a Voting System
    """
    
    class Ballot(ABC):
        """
        Abstract Ballot Class
        Represents a Ballot in the Voting System
        """
        
        def __init__(self, scores):
            """
            Initializes a ballot in this voting system. 
            
            Parameters
            scores
                a representation of the ballot interpretable by this voting
                system
            """
            self.scores = scores.copy()
        
        def isValid(self, try_handle_invalid=True):
            """
            Checks if this ballot is valid. 
            
            Parameters
            try_handle_invalid : bool, default=True
                whether we attempt to fix ballots that seems invalid
            
            Returns
            bool
                whether this ballot is valid
            """
            pass
        
        def Vote(self, candidates):
            """
            Expresses this ballot's opinions on the candidates. 
            isValid must be called first and has returned True. 
            
            Parameters
            candidates : list
                an non-empty list of unique strings representing the candidates
            
            Returns
            pandas.Series
                a Series of numeric values with candidates as the index,
                representing this ballot's preferences of the candidates
            """
            pass
        
        def Export(self, candidates):
            """
            Exports this ballot in the format to be saved in a file. 
            isValid must be called first and has returned True. 
            
            Parameters
            candidates : list
                an non-empty list of unique strings representing the candidates
            
            Returns
                a represention of this ballot in a format interpretable
                by this voting system
            """
            pass
            
    def __init__(self, candidates, try_handle_invalid=True):
        """
        Initializes an election using this voting system. 
        
        Parameters
        candidates : list
            an non-empty list of unique strings representing the candidates
        try_handle_invalid : bool, default=True
            whether we attempt to fix ballots that seems invalid
        """
        self.candidates = candidates
        self.try_handle_invalid = try_handle_invalid
        self.ballots = []
    
    def AddBallot(self, new_ballot):
        """
        Adds a ballot to the election if it is valid. 
        
        Parameters
        new_ballot
            a representation of the ballot interpretable by this voting system
        
        Returns
        bool
            whether this ballot is valid and added successfully
        """
        pass
    
    def ImportBallots(self, filename):
        """
        Imports ballots from a file to the election. 
        
        Parameters
        filename : str
            name of the ballot file to be imported, possibly the full path
        
        Returns
        int
            number of valid ballots successfully added
        """
        df = pd.read_excel(filename, index_col=0)
        old_ballot_cnt = len(self.ballots)
        for i in df.index:
            self.AddBallot(df.loc[i])
        return len(self.ballots)-old_ballot_cnt
    
    def ExportBallots(self, filename):
        """
        Exports all valid ballots in this election to a file. 
        
        Parameters
        filename : str
            name of the ballot file to be exported to, possibly the full path
        
        Returns
        int
            number of valid ballots successfully exported
        """
        df = pd.DataFrame(columns=self.candidates)
        for b in self.ballots:
            df = pd.concat([df, b.Export(self.candidates).to_frame().T], 
                           ignore_index=True)
        df.to_excel(filename)
        return df.shape[0]
    
    def RunElection(self, candidates=None):
        """
        Runs the election with the given candidates and get the results. 
        
        Parameters
        candidates : list, default=None
            a list of unique strings representing the candidates
            if None, all candidates specified in constructor will be included
        
        Returns
        list
            a list of (candidate, rank, log) tuples representing the election
            result, ordered by rank from first to last, possibly with ties
            log is a list of (score, outcome) tuples each representing the 
            candidate's result of a round of election in chronological order, 
            where outcome can be "u", "l", or "t", representing the candidate
            ended up in the upper bracket, lower bracket, or tied, respectively
        """
        if candidates==None:
            candidates=self.candidates
        if candidates==[]:
            return []
        # add up scores from all ballots
        scores = pd.Series(data=0, index=candidates)
        for b in self.ballots:
            scores += b.Vote(candidates)
        # if everyone ties for the first place, do not recurse anymore
        if scores.max()==scores.min():
            return [(c, 1, [(scores[c], "t")]) for c in candidates]
        # split the candidates into an upper bracket and a lower bracket
        scores.sort_values(inplace=True, ascending=False)
        cutoff_rank = self.SplitSize(len(scores))
        cutoff_score = (scores[cutoff_rank-1]+scores[cutoff_rank])/2
        upper_bracket = [c for c in candidates if scores[c]>cutoff_score]
        lower_bracket = [c for c in candidates if scores[c]<cutoff_score]
        # add candidates with score equal to the cutoff to the smaller bracket
        # this ensures neither bracket is empty, thus preventing infinite
        # recursion
        if len(upper_bracket)<=len(lower_bracket):
            upper_bracket += [c for c in candidates if scores[c]==cutoff_score]
        else:
            lower_bracket += [c for c in candidates if scores[c]==cutoff_score]
        # recursively run elections on two groups of candidates, then merge
        result = []
        upper_result = self.RunElection(upper_bracket)
        lower_result = self.RunElection(lower_bracket)
        for (c, r, l) in upper_result:
            result.append((c, r, [(scores[c], "u")]+l))
        for (c, r, l) in lower_result:
            result.append((c, r+len(upper_bracket), [(scores[c], "l")]+l))
        return result
    
    def SplitSize(self, num_candidates):
        """
        Calculates how many candidates will be placed in the upper bracket. 
        Actual bracket sizes used may be different due to ties. 
        
        Parameters
        num_candidates : int
            total number of candidates to be splited
        
        Returns
        int
            number of candidates to be placed in the upper bracket
        """
        return num_candidates-1
    
