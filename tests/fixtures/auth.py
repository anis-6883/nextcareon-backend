"""tests/fixtures/auth.py - Authentication test fixtures."""



def generate_mock_jwt_token(user_id: str, role: str) -> str:
    """
    Generate a mock JWT token for testing.
    In production, use actual JWT creation.
    """
    from app.core.security import create_access_token
    return create_access_token(user_id, role=role)


async def create_test_student(session, user_id: str = None, email: str = "student@test.com"):
    """Create a test student in the database."""
    from app.modules.users.models import Student
    from app.core.security import hash_password

    student = Student(
        id=user_id or "student-123",
        full_name="Test Student",
        email=email,
        password_hash=hash_password("Password123!"),
    )
    session.add(student)
    await session.commit()
    await session.refresh(student)
    return student


async def create_test_admin(session, user_id: str = None, email: str = "admin@test.com", role: str = "content_manager"):
    """Create a test admin in the database."""
    from app.modules.users.models import AdminUser, UserRole
    from app.core.security import hash_password

    admin_role = UserRole.SUPER_ADMIN if role == "super_admin" else UserRole.CONTENT_MANAGER
    admin = AdminUser(
        id=user_id or "admin-123",
        full_name="Test Admin",
        email=email,
        password_hash=hash_password("Password123!"),
        role=admin_role,
    )
    session.add(admin)
    await session.commit()
    await session.refresh(admin)
    return admin