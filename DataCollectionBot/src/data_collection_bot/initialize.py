import pandas as pd

from src.data_collection_bot import UserService, User, Roles, RoleService, Role, CreateRoleDTO, \
    InviteService, ParameterService, CreateParameterDTO, Parameter, Rules
from src.data_collection_bot.config import PARAMETERS_TABLE_PATH, ADMIN_INVITE_FILE_PATH


async def initialize(
        user_service: UserService,
        role_service: RoleService,
        invite_service: InviteService,
        parameter_service: ParameterService,
        admin_telegram_id: int,
):
    await ensure_roles_exists(role_service=role_service)
    await add_parameters_from_xlsx(
        parameter_service=parameter_service,
        role_service=role_service
    )
    await ensure_admin_user_exists(
        user_service=user_service,
        role_service=role_service,
        invite_service=invite_service,
        admin_telegram_id=admin_telegram_id,
    )



async def ensure_roles_exists(
        role_service: RoleService
):
    for role in Roles:
        name = role.value
        exists = await role_service.get_role_by_name(name=name)
        if exists is None:
            new_role = CreateRoleDTO(name=name)
            await role_service.create(new_role)


async def ensure_admin_user_exists(
        user_service: UserService,
        role_service: RoleService,
        invite_service: InviteService,
        admin_telegram_id: int,
):
    admin: User = await user_service.get_user_by_telegram_id(admin_telegram_id)
    if admin is None:
        role: Role = await role_service.get_role_by_name(Roles.ADMIN.value)

        link: str = await invite_service.generate_invite_link(role=role)
        with open(ADMIN_INVITE_FILE_PATH, 'w') as file:
            file.write(link)
            file.close()


async def add_parameters_from_xlsx(
        parameter_service: ParameterService,
        role_service: RoleService
):
    df = pd.read_excel(PARAMETERS_TABLE_PATH)

    for index, row in df.iterrows():
        name = str(row['name'])
        roles = str(row['roles'])
        rule = str(row['rule'])
        choice = str(row['choice']) if pd.notna(row['choice']) else None
        norm_row = str(row['norm_row'])
        instruction = str(row['instruction']) if pd.notna(row['instruction']) else None

        parameter_dtp = CreateParameterDTO(name=name, rule=Rules(rule).name, choice=choice, norm_row=norm_row, instruction=instruction)
        parameter: Parameter = await parameter_service.create(parameter_dtp)

        roles_list: list[Role] = [(await role_service.get_role_by_name(name)) for name in roles.split(', ')]
        for role in roles_list:
            await role_service.add_parameter_to_role(role_id=role.id, parameter_id=parameter.id)
