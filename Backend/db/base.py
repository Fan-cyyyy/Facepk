# 导入基础Base类
from config.database import Base

# 注释掉模型导入，避免循环导入
# 这些导入只是为了让Alembic能够发现模型
# from models.user import User
# from models.score import Score
# from models.match import Match
# from models.friend import UserFriend
# from models.stats import UserStats 