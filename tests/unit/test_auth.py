"""tests/unit/test_auth.py - Authentication and admin authorization tests."""

import pytest
from httpx import AsyncClient
from app.utils.validators import validate_password_strength, PasswordStrengthError


class TestPasswordValidation:
    """Test strong password validation."""

    def test_valid_password(self):
        """Valid password should pass validation."""
        assert validate_password_strength("Password123!") == "Password123!"

    def test_password_too_short(self):
        """Password shorter than 8 characters should fail."""
        with pytest.raises(PasswordStrengthError):
            validate_password_strength("Pass1!")

    def test_password_no_uppercase(self):
        """Password without uppercase should fail."""
        with pytest.raises(PasswordStrengthError):
            validate_password_strength("password123!")

    def test_password_no_lowercase(self):
        """Password without lowercase should fail."""
        with pytest.raises(PasswordStrengthError):
            validate_password_strength("PASSWORD123!")

    def test_password_no_digit(self):
        """Password without digit should fail."""
        with pytest.raises(PasswordStrengthError):
            validate_password_strength("Password!")

    def test_password_no_special(self):
        """Password without special character should fail."""
        with pytest.raises(PasswordStrengthError):
            validate_password_strength("Password123")


class TestAdminAuthorization:
    """Test admin endpoint authorization."""

    @pytest.mark.asyncio
    async def test_admin_cannot_access_without_token(self, test_client: AsyncClient):
        """Admin endpoints should reject requests without token."""
        response = await test_client.get("/api/v1/admin/students")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_student_cannot_access_admin_endpoints(self, test_client: AsyncClient, async_session):
        """Student users should receive 403 when accessing admin endpoints."""
        from tests.fixtures.auth import create_test_student, generate_mock_jwt_token

        student = await create_test_student(async_session)
        token = generate_mock_jwt_token(student.id, role="student")

        response = await test_client.get(
            "/api/v1/admin/students",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_admin_can_list_students(self, test_client: AsyncClient, async_session):
        """Admin users should be able to list students."""
        from tests.fixtures.auth import create_test_admin, create_test_student, generate_mock_jwt_token

        await create_test_student(async_session, user_id="student-1")
        admin = await create_test_admin(async_session)
        token = generate_mock_jwt_token(admin.id, role="admin")

        response = await test_client.get(
            "/api/v1/admin/students",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_non_super_admin_cannot_delete_student(self, test_client: AsyncClient, async_session):
        """Regular admin should not be able to delete students (requires super admin)."""
        from tests.fixtures.auth import create_test_admin, create_test_student, generate_mock_jwt_token

        student = await create_test_student(async_session, user_id="student-to-delete")
        admin = await create_test_admin(async_session, role="content_manager")
        token = generate_mock_jwt_token(admin.id, role="admin")

        response = await test_client.delete(
            f"/api/v1/admin/students/{student.id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_super_admin_can_delete_student(self, test_client: AsyncClient, async_session):
        """Super admin should be able to delete students."""
        from tests.fixtures.auth import create_test_admin, create_test_student, generate_mock_jwt_token
        from sqlmodel import select
        from app.modules.users.models import Student

        student = await create_test_student(async_session, user_id="student-to-delete")
        admin = await create_test_admin(async_session, role="super_admin")
        token = generate_mock_jwt_token(admin.id, role="admin")

        response = await test_client.delete(
            f"/api/v1/admin/students/{student.id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 204

        result = await async_session.execute(select(Student).where(Student.id == "student-to-delete"))
        assert result.first() is None
