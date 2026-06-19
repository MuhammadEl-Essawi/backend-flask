using System.Net;
using System.Text.Json;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.Logging;
using Microsoft.Data.SqlClient;
using Microsoft.EntityFrameworkCore;

namespace Rently.Management.WebApi.Middleware
{
    public class ExceptionMiddleware
    {
        private readonly RequestDelegate _next;
        private readonly ILogger<ExceptionMiddleware> _logger;
        private readonly IHostEnvironment _env;

        public ExceptionMiddleware(RequestDelegate next, ILogger<ExceptionMiddleware> logger, IHostEnvironment env)
        {
            _next = next;
            _logger = logger;
            _env = env;
        }

        public async Task InvokeAsync(HttpContext context)
        {
            try
            {
                await _next(context);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, ex.Message);
                context.Response.ContentType = "application/json";
                
                var statusCode = (int)HttpStatusCode.InternalServerError;
                var message = "An unexpected error occurred.";

                // Professional Handling for specific exception types
                switch (ex)
                {
                    case UnauthorizedAccessException:
                        statusCode = (int)HttpStatusCode.Unauthorized;
                        message = "You are not authorized to access this resource.";
                        break;
                    case KeyNotFoundException:
                        statusCode = (int)HttpStatusCode.NotFound;
                        message = "The requested resource was not found.";
                        break;
                    case DbUpdateException dbEx:
                        statusCode = (int)HttpStatusCode.BadRequest;
                        message = "A database error occurred. Please check your data constraints.";
                        // Log more details internally but don't expose all to client
                        break;
                    case InvalidOperationException:
                        statusCode = (int)HttpStatusCode.BadRequest;
                        message = ex.Message;
                        break;
                }

                context.Response.StatusCode = statusCode;

                var response = _env.IsDevelopment()
                    ? new ApiException(statusCode, ex.Message, ex.StackTrace?.ToString())
                    : new ApiException(statusCode, message);

                var options = new JsonSerializerOptions { PropertyNamingPolicy = JsonNamingPolicy.CamelCase };
                var json = JsonSerializer.Serialize(response, options);

                await context.Response.WriteAsync(json);
            }
        }
    }

    public class ApiException
    {
        public ApiException(int statusCode, string message, string? details = null)
        {
            StatusCode = statusCode;
            Message = message;
            Details = details;
        }

        public int StatusCode { get; set; }
        public string Message { get; set; }
        public string? Details { get; set; }
    }
}
