"""
Utility functions for consistent API responses.

Every API endpoint should use these helpers to return
standardized JSON responses.
"""

from rest_framework.response import Response
from rest_framework import status


class APIResponse:
    """
    Standardized API response helper.

    Usage:
        return APIResponse.success(data={'key': 'value'}, message='Done')
        return APIResponse.error(message='Something failed', status_code=400)
        return APIResponse.paginated(data=serializer.data, page_info={...})
    """

    @staticmethod
    def success(data=None, message='Success', status_code=200):
        """Return successful response with data"""
        return Response(
            {
                'success': True,
                'message': message,
                'data': data or {},
            },
            status=status_code
        )

    @staticmethod
    def created(data=None, message='Created successfully'):
        """Return 201 Created response"""
        return Response(
            {
                'success': True,
                'message': message,
                'data': data or {},
            },
            status=status.HTTP_201_CREATED
        )

    @staticmethod
    def error(message='An error occurred', errors=None, status_code=400):
        """Return error response"""
        return Response(
            {
                'success': False,
                'message': message,
                'errors': errors or {},
            },
            status=status_code
        )

    @staticmethod
    def not_found(message='Resource not found'):
        """Return 404 Not Found response"""
        return Response(
            {
                'success': False,
                'message': message,
                'errors': {},
            },
            status=status.HTTP_404_NOT_FOUND
        )

    @staticmethod
    def paginated(data, pagination_info, message='Success'):
        """Return paginated list response"""
        return Response(
            {
                'success': True,
                'message': message,
                'data': data,
                'pagination': pagination_info,
            },
            status=status.HTTP_200_OK
        )

    @staticmethod
    def validation_error(errors, message='Validation failed'):
        """Return validation error response"""
        return Response(
            {
                'success': False,
                'message': message,
                'errors': errors,
            },
            status=status.HTTP_422_UNPROCESSABLE_ENTITY
        )
