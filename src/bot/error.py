class ScoreboardError(Exception):
    pass


class FetchError(ScoreboardError):
    pass


class ParseError(ScoreboardError):
    pass
