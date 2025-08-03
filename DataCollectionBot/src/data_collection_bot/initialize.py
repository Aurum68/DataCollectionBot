from src.data_collection_bot import UserService, User, Roles, RoleService, Role, CreateRoleDTO, \
    InviteService


async def initialize(
        user_service: UserService,
        role_service: RoleService,
        invite_service: InviteService,
        admin_telegram_id: int,
):
    await ensure_roles_exists(role_service=role_service)
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
        print("Ссылка для входа админа: ", link)