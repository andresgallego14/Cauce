from database import Base
from database import engine
import models
Base.metadata. create_all(engine)