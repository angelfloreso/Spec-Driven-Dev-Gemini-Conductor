from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=3, max_length=200)


class AuthTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    user_id: int
    linked_patient_id: int | None = None
    linked_practitioner_id: int | None = None


class CurrentUserRead(BaseModel):
    id: int
    username: str
    role: str
    patient_id: int | None = None
    practitioner_id: int | None = None

    model_config = {"from_attributes": True}
