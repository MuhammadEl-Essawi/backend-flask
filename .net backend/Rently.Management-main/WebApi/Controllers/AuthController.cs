using Microsoft.AspNetCore.Mvc;
using Microsoft.IdentityModel.Tokens;
using Rently.Management.Domain.Repositories;
using Rently.Management.WebApi.DTOs;
using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using System.Text;
using Rently.Management.WebApi.Services;

namespace Rently.Management.WebApi.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class AuthController : ControllerBase
    {
        /// <summary>
        /// JWT authentication: login and issue a token for protected routes.
        /// </summary>
        private readonly IUserRepository _userRepository;
        private readonly IConfiguration _configuration;
        private readonly PasswordService _passwordService;

        public AuthController(IUserRepository userRepository, IConfiguration configuration, PasswordService passwordService)
        {
            _userRepository = userRepository;
            _configuration = configuration;
            _passwordService = passwordService;
        }

        [HttpPost("login")]
        [Microsoft.AspNetCore.Authorization.AllowAnonymous]
        /// <summary>
        /// Admin development login using settings (Admin:Email/Admin:Password) and issues a JWT.
        /// Also supports DB-based Admin login using stored password hash/salt.
        /// Returns claims (Name/Email/Role/UserId) inside the token.
        /// </summary>
        public async Task<ActionResult<LoginResponseDto>> Login([FromBody] LoginRequestDto dto)
        {
            if (string.IsNullOrWhiteSpace(dto.Email))
                return BadRequest();

            var user = await _userRepository.GetByEmailAsync(dto.Email);
            if (user == null)
                return Unauthorized();

            var adminEmail = _configuration["Admin:Email"] ?? "";
            var adminPassword = _configuration["Admin:Password"] ?? "";
            var providedPassword = dto.Password ?? "";

            var isAdminRole = string.Equals(user.Role, "Admin", StringComparison.OrdinalIgnoreCase);
            if (!isAdminRole) return Unauthorized();

            var devLoginOK = user.Email!.Equals(adminEmail, StringComparison.OrdinalIgnoreCase) && providedPassword == adminPassword;
            var dbLoginOK = false;
            if (!string.IsNullOrEmpty(user.PasswordHash) && !string.IsNullOrEmpty(user.PasswordSalt))
            {
                dbLoginOK = _passwordService.Verify(providedPassword, user.PasswordHash!, user.PasswordSalt!);
            }

            if (!(devLoginOK || dbLoginOK))
                return Unauthorized();

            var issuer = _configuration["Jwt:Issuer"] ?? "";
            var audience = _configuration["Jwt:Audience"] ?? "";
            var key = _configuration["Jwt:Key"] ?? "";
            var expiresMinutes = int.TryParse(_configuration["Jwt:ExpiresMinutes"], out var m) ? m : 60;

            var claims = new List<Claim>
            {
                new Claim(JwtRegisteredClaimNames.Sub, user.Id.ToString()),
                new Claim(JwtRegisteredClaimNames.Email, user.Email ?? ""),
                new Claim("is_super_admin", user.IsSuperAdmin.ToString().ToLower()),
                new Claim(ClaimTypes.Name, $"{user.FirstName} {user.LastName}".Trim()),
                new Claim(ClaimTypes.Role, user.Role ?? "User")
            };

            var securityKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(key));
            var credentials = new SigningCredentials(securityKey, SecurityAlgorithms.HmacSha256);
            var token = new JwtSecurityToken(
                issuer: issuer,
                audience: audience,
                claims: claims,
                expires: DateTime.UtcNow.AddMinutes(expiresMinutes),
                signingCredentials: credentials
            );

            var tokenString = new JwtSecurityTokenHandler().WriteToken(token);
            return Ok(new LoginResponseDto
            {
                Token = tokenString,
                FirstName = user.FirstName,
                LastName = user.LastName,
                Email = user.Email,
                Role = user.Role,
                IsSuperAdmin = user.IsSuperAdmin,
                UserId = user.Id
            });
        }
    }
}
