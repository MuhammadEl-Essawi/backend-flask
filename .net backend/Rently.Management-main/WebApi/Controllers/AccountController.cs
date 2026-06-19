using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Rently.Management.WebApi.DTOs;
using Rently.Management.WebApi;
using Rently.Management.WebApi.Services;

namespace Rently.Management.WebApi.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class AccountController : ControllerBase
    {
        /// <summary>
        /// Admin account management: change name/password, request/reset password, add admin.
        /// </summary>
        private readonly ApplicationDbContext _context;
        private readonly PasswordService _passwordService;
        private readonly WebhookService _webhookService;
        private readonly IEmailService _emailService;

        public AccountController(ApplicationDbContext context, PasswordService passwordService, WebhookService webhookService, IEmailService emailService)
        {
            _context = context;
            _passwordService = passwordService;
            _webhookService = webhookService;
            _emailService = emailService;
        }

        [HttpPost("change-name")]
        [Authorize]
        /// <summary>
        /// Update current user's display name using the JWT 'sub' claim.
        /// </summary>
        public async Task<IActionResult> ChangeName([FromBody] ChangeNameDto dto)
        {
            var sub = User.FindFirst(System.IdentityModel.Tokens.Jwt.JwtRegisteredClaimNames.Sub)?.Value;
            if (!int.TryParse(sub, out var userId)) return Unauthorized();
            var user = await _context.Users.FindAsync(userId);
            if (user == null) return NotFound();
            user.FirstName = dto.FirstName;
            user.LastName = dto.LastName;
            user.UpdatedAt = DateTime.UtcNow;
            _context.Users.Update(user);
            await _context.SaveChangesAsync();
            _ = _webhookService.PublishAsync("user.updated", new { user_id = user.Id, first_name = user.FirstName, last_name = user.LastName, email = user.Email });
            return NoContent();
        }

        [HttpPost("change-password")]
        [Authorize]
        /// <summary>
        /// Change password after verifying the current one; store new hash and salt.
        /// </summary>
        public async Task<IActionResult> ChangePassword([FromBody] ChangePasswordDto dto)
        {
            var sub = User.FindFirst(System.IdentityModel.Tokens.Jwt.JwtRegisteredClaimNames.Sub)?.Value;
            if (!int.TryParse(sub, out var userId)) return Unauthorized();
            var user = await _context.Users.FindAsync(userId);
            if (user == null) return NotFound();
            if (string.IsNullOrEmpty(user.PasswordHash) || string.IsNullOrEmpty(user.PasswordSalt)) return BadRequest();
            var ok = _passwordService.Verify(dto.CurrentPassword, user.PasswordHash!, user.PasswordSalt!);
            if (!ok) return Unauthorized();
            var pair = _passwordService.HashPassword(dto.NewPassword);
            user.PasswordHash = pair.hash;
            user.PasswordSalt = pair.salt;
            user.UpdatedAt = DateTime.UtcNow;
            _context.Users.Update(user);
            await _context.SaveChangesAsync();
            _ = _webhookService.PublishAsync("user.password_changed", new { user_id = user.Id, email = user.Email });
            return NoContent();
        }

        [HttpPost("request-reset")]
        [AllowAnonymous]
        /// <summary>
        /// Request password reset: create a temporary token valid for 30 minutes.
        /// </summary>
        public async Task<IActionResult> RequestReset([FromBody] RequestResetDto dto, [FromQuery] bool debug = false)
        {
            var email = dto.Email.Trim().ToLowerInvariant();
            var user = _context.Users.FirstOrDefault(u => (u.Email ?? "").ToLower() == email);
            if (user == null) return NoContent();

            // Generate 6-digit OTP
            var otp = new Random().Next(100000, 999999).ToString();
            user.PasswordResetToken = otp; // We reuse this column for OTP
            user.PasswordResetTokenExpires = DateTime.UtcNow.AddMinutes(10); // OTP expires in 10 minutes
            user.UpdatedAt = DateTime.UtcNow;
            _context.Users.Update(user);
            await _context.SaveChangesAsync();

            try
            {
                await _emailService.SendEmailAsync(user.Email!, "Password Reset OTP", $"Your OTP for password reset is: <b>{otp}</b>. It will expire in 10 minutes.");
            }
            catch (Exception ex)
            {
                // In a real app, log the error. For now, if we're in debug, return it.
                if (debug) return StatusCode(500, new { message = "Failed to send email", error = ex.Message });
            }

            if (debug)
            {
                var env = HttpContext.RequestServices.GetRequiredService<IWebHostEnvironment>();
                if (string.Equals(env.EnvironmentName, "Development", StringComparison.OrdinalIgnoreCase))
                {
                    return Ok(new { message = "Reset requested", dev_token = otp });
                }
            }
            return Ok(new { message = "Reset requested" });
        }

        [HttpPost("reset-password")]
        [AllowAnonymous]
        /// <summary>
        /// Reset password using the temporary token, then clear it after update.
        /// </summary>
        public async Task<IActionResult> ResetPassword([FromBody] ResetPasswordDto dto)
        {
            var email = dto.Email.Trim().ToLowerInvariant();
            var user = _context.Users.FirstOrDefault(u => (u.Email ?? "").ToLower() == email);
            if (user == null) return NotFound();
            if (user.PasswordResetToken != dto.Token || user.PasswordResetTokenExpires == null || user.PasswordResetTokenExpires < DateTime.UtcNow)
                return Unauthorized();
            var pair = _passwordService.HashPassword(dto.NewPassword);
            user.PasswordHash = pair.hash;
            user.PasswordSalt = pair.salt;
            user.PasswordResetToken = null;
            user.PasswordResetTokenExpires = null;
            user.UpdatedAt = DateTime.UtcNow;
            _context.Users.Update(user);
            await _context.SaveChangesAsync();
            return NoContent();
        }

        private static readonly Dictionary<string, (string otp, DateTime expires)> _adminOtps = new();

        [HttpPost("request-admin-otp")]
        [Authorize(Roles = "Admin")]
        /// <summary>
        /// Request OTP to add a new admin.
        /// </summary>
        public async Task<IActionResult> RequestAdminOtp([FromBody] RequestAddAdminOtpDto dto)
        {
            var sub = User.FindFirst(System.IdentityModel.Tokens.Jwt.JwtRegisteredClaimNames.Sub)?.Value;
            if (!int.TryParse(sub, out var currentUserId)) return Unauthorized();
            var currentUser = await _context.Users.FindAsync(currentUserId);
            if (currentUser == null || !currentUser.IsSuperAdmin) return Forbid();

            var email = dto.Email.Trim().ToLowerInvariant();
            var exists = _context.Users.Any(u => (u.Email ?? "").ToLower() == email);
            if (exists) return Conflict(new { message = "Email already exists." });

            var otp = new Random().Next(100000, 999999).ToString();
            _adminOtps[email] = (otp, DateTime.UtcNow.AddMinutes(10));

            try
            {
                await _emailService.SendEmailAsync(email, "New Admin Verification OTP", $"Your OTP for admin registration is: <b>{otp}</b>. It will expire in 10 minutes.");
                return Ok(new { message = "OTP sent successfully." });
            }
            catch (Exception ex)
            {
                return StatusCode(500, new { message = "Failed to send email", error = ex.Message });
            }
        }

        [HttpPost("add-admin")]
        [Authorize(Roles = "Admin")]
        /// <summary>
        /// Add a new admin user (requires Role=Admin in the JWT and valid OTP).
        /// </summary>
        public async Task<IActionResult> AddAdmin([FromBody] AddAdminDto dto)
        {
            var sub = User.FindFirst(System.IdentityModel.Tokens.Jwt.JwtRegisteredClaimNames.Sub)?.Value;
            if (!int.TryParse(sub, out var currentUserId)) return Unauthorized();
            var currentUser = await _context.Users.FindAsync(currentUserId);
            if (currentUser == null || !currentUser.IsSuperAdmin) return Forbid();

            var email = dto.Email.Trim().ToLowerInvariant();
            
            // Verify OTP
            if (!_adminOtps.TryGetValue(email, out var otpData) || otpData.otp != dto.Otp || otpData.expires < DateTime.UtcNow)
            {
                return BadRequest(new { message = "Invalid or expired OTP." });
            }
            _adminOtps.Remove(email); // Remove after use

            var exists = _context.Users.Any(u => (u.Email ?? "").ToLower() == email);
            if (exists) return Conflict();

            var pair = _passwordService.HashPassword(dto.Password);
            var user = new Rently.Management.Domain.Entities.User
            {
                FirstName = dto.FirstName,
                LastName = dto.LastName,
                Email = dto.Email,
                Phone = dto.Phone,
                Role = "Admin",
                ApprovalStatus = "Approved",
                PasswordHash = pair.hash,
                PasswordSalt = pair.salt,
                CreatedAt = DateTime.UtcNow
            };
            _context.Users.Add(user);
            await _context.SaveChangesAsync();
            _ = _webhookService.PublishAsync("user.created", new { user_id = user.Id, first_name = user.FirstName, last_name = user.LastName, email = user.Email, role = user.Role });
            return CreatedAtAction(nameof(AddAdmin), new { id = user.Id }, new { id = user.Id });
        }
    }
}
