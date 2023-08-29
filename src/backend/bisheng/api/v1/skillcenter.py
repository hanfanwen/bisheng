from bisheng.api.utils import remove_api_keys
from bisheng.database.base import get_session
from bisheng.database.models.template import (Template, TemplateCreate,
                                              TemplateRead, TemplateUpdate)
from bisheng.settings import settings
from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlmodel import Session, select

# build router
router = APIRouter(prefix='/skill', tags=['Skills'])


@router.post('/template/create', response_model=TemplateRead, status_code=201)
def create_template(*, session: Session = Depends(get_session), template: TemplateCreate):
    """Create a new flow."""
    db_template = Template.from_orm(template)
    session.add(db_template)
    session.commit()
    session.refresh(db_template)
    return db_template


@router.get('/template/', response_model=list[Template], status_code=200)
def read_template(*, session: Session = Depends(get_session)):
    """Read all flows."""
    try:
        templates = session.exec(select(Template)).all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    return [jsonable_encoder(temp) for temp in templates]


@router.post('/template/{id}', response_model=TemplateRead, status_code=200)
def update_template(*, session: Session = Depends(get_session), id: int, template: TemplateUpdate):
    """Update a flow."""
    db_template = session.get(Template, id)
    if not db_template:
        raise HTTPException(status_code=404, detail='Template not found')
    template_data = template.dict(exclude_unset=True)
    if settings.remove_api_keys:
        template_data = remove_api_keys(template_data)
    for key, value in template_data.items():
        setattr(db_template, key, value)
    session.add(db_template)
    session.commit()
    session.refresh(db_template)
    return db_template