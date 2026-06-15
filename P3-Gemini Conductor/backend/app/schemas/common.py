from datetime import date, datetime, time

from pydantic import BaseModel, EmailStr, Field


class SpecialtyCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)


class SpecialtyRead(SpecialtyCreate):
    id: int

    model_config = {"from_attributes": True}


class PractitionerCreate(BaseModel):
    full_name: str = Field(min_length=3, max_length=150)
    email: EmailStr
    specialty_id: int


class PractitionerRead(PractitionerCreate):
    id: int

    model_config = {"from_attributes": True}


class ShiftCreate(BaseModel):
    practitioner_id: int
    weekday: int = Field(ge=0, le=6)
    start_time: time
    end_time: time


class ShiftRead(ShiftCreate):
    id: int

    model_config = {"from_attributes": True}


class HolidayCreate(BaseModel):
    holiday_date: date
    label: str = Field(min_length=2, max_length=150)


class HolidayRead(HolidayCreate):
    id: int

    model_config = {"from_attributes": True}


class BlockCreate(BaseModel):
    practitioner_id: int | None = None
    start_datetime: datetime
    end_datetime: datetime
    reason: str = Field(default="Unavailable", max_length=250)


class BlockRead(BlockCreate):
    id: int

    model_config = {"from_attributes": True}


class PatientCreate(BaseModel):
    full_name: str = Field(min_length=3, max_length=150)
    date_of_birth: date
    biological_sex: str = Field(min_length=1, max_length=30)
    phone_number: str = Field(min_length=7, max_length=30)
    email: EmailStr
    known_allergies: str = Field(default="", max_length=500)
    government_id: str = Field(min_length=3, max_length=50)


class PatientRead(PatientCreate):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}
