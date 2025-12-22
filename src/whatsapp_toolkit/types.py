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
    
    def __str__(self) -> str:
        texto = f"Group ID: {self.id}\n"
        texto += f" Subject: {self.subject}\n"
        texto += f" Kind: {self.kind}\n"
        texto += f" Size: {self.size} participantes\n"
        texto += f" Created at: {self.creation}\n"
        texto += f" Restrict: {self.restrict}\n"
        texto += f" Announce: {self.announce}\n"
        texto += f" Participants:\n"
        for p in self.participants:
            texto += f"   - ID: {p.id} | Admin: {p.admin}\n"
        return texto



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
    
    
    def get_group_by_id(self, group_id: str) -> Optional[GroupBase]:
        for group in self.groups:
            if group.id == group_id:
                return group
        return None
    
    
    def get_gruop_by_subject(self, subject: str) -> Optional[GroupBase]:
        for group in self.groups:
            if group.subject == subject:
                return group
        return None
    
    
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
    
    def __len__(self):
        return len(self.groups)
    
    def __str__(self) -> str:
        texto = f"Groups: {len(self.groups)} grupos cargados.\n"
        texto += f"Fails: {len(self.fails)} grupos con errores de validación.\n"
        return texto