from typing import Optional, Literal
from pydantic import BaseModel, ValidationError

# =============================
# MODELOS DE DATOS
# =============================
class Participant(BaseModel):
    id: str
    admin: Optional[str] = None          # "admin" | "superadmin" | None
    phoneNumber: Optional[str] = None    # a veces no viene ojito

    @property
    def is_admin(self) -> bool:
        return self.admin == "admin"

    @property
    def is_superadmin(self) -> bool:
        return self.admin == "superadmin"


class GroupBase(BaseModel):
    # obligatorios
    id: str
    subject: str
    subjectTime: int
    pictureUrl: Optional[str] = None
    size: int
    creation: int
    restrict: bool
    announce: bool
    isCommunity: bool
    isCommunityAnnounce: bool
    participants: list[Participant]
    
    # opcionales (por tus variantes)
    owner: Optional[str] = None
    subjectOwner: Optional[str] = None
    desc: Optional[str] = None
    descId: Optional[str] = None
    linkedParent: Optional[str] = None
    
    
    @property
    def kind(self) -> Literal["community_root", "community_announce_child", "regular_group", "unknown"]:
        if self.isCommunity:
            return "community_root"

        if self.isCommunityAnnounce or self.linkedParent is not None:
            return "community_announce_child"

        if (not self.isCommunity) and (not self.isCommunityAnnounce):
            return "regular_group"

        return "unknown"



class Groups(BaseModel):
    groups: list[GroupBase] = []
    fails: list[tuple[Optional[str], Optional[str], str]] = []
    
    
    def upload_groups(self, groups_raw: list[dict]) -> None:
        for group in groups_raw:
            try:
                self.groups.append(GroupBase.model_validate(group))
            except ValidationError as e:
                self.fails.append((group.get("id"),group.get("subject"),str(e)))
    
    
    def count_by_kind(self) -> dict[str, int]:
        kind_counter = {}
        for g in self.groups:
            k = g.kind
            kind_counter[k] = kind_counter.get(k, 0) + 1
        return kind_counter
    
    
    def search_group(self, query: str, limit: int = 10):
        q = query.strip().lower()
        
        tokens = [token for token in q.split() if token]
        scored = []
        finded_groups: list[GroupBase] = []
        for group in self.groups:
            subject = (group.subject or "").lower()
            score = 0
            
            # Si es match exacto
            if q in subject:
                score += 2
            
            # Por cada token presente
            for token in tokens:
                if token in subject:
                    score += 1
            
            # Si hay puntos se agrega
            if score > 0:
                scored.append((score,group))
            
            # Ordenamos por puntiaje
            scored.sort(key=lambda x: x[0], reverse=True)
            
            finded_groups = [group for score, group in scored]
        return finded_groups[:limit]