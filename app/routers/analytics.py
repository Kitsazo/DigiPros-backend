from fastapi import APIRouter, Depends

from ..deps import get_current_user
from ..models import User
from ..schemas import AnalyticsOut, AnalyticsPoint

router = APIRouter(prefix="/analytics", tags=["analytics"])


_DEFAULT_HISTORY: list[AnalyticsPoint] = [
    AnalyticsPoint(label="Jan", spent=4200, returned=11900),
    AnalyticsPoint(label="Feb", spent=4800, returned=14100),
    AnalyticsPoint(label="Mar", spent=5300, returned=16800),
    AnalyticsPoint(label="Apr", spent=6200, returned=18900),
    AnalyticsPoint(label="May", spent=7100, returned=23700),
    AnalyticsPoint(label="Jun", spent=8400, returned=29100),
]


@router.get("/me", response_model=AnalyticsOut)
def my_analytics(_user: User = Depends(get_current_user)) -> AnalyticsOut:
    """Returns a placeholder analytics snapshot.

    Wired to a static payload for now — once we plug in real reporting
    (GA4, ad platforms, attribution) we can swap this out without the
    frontend having to change.
    """
    spent = sum(p.spent for p in _DEFAULT_HISTORY)
    returned = sum(p.returned for p in _DEFAULT_HISTORY)
    roas = round(returned / spent, 2) if spent else 0.0
    return AnalyticsOut(
        total_spent=spent,
        total_returned=returned,
        roas=roas,
        active_campaigns=6,
        leads_this_month=148,
        impressions=482_300,
        clicks=18_420,
        conversions=312,
        history=_DEFAULT_HISTORY,
    )
