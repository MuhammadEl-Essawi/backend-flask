using Microsoft.AspNetCore.Mvc;
using Rently.Management.Domain.Entities;
using Rently.Management.Domain.Repositories;
using Rently.Management.WebApi.DTOs;
using Microsoft.AspNetCore.Authorization;

namespace Rently.Management.WebApi.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    [Authorize]
    public class UserController : ControllerBase
    {
        private readonly IUserRepository _userRepository;

        public UserController(IUserRepository userRepository)
        {
            _userRepository = userRepository;
        }

        [HttpGet]
        public async Task<ActionResult<PagedResultDto<UserDto>>> GetUsers(
            [FromQuery] string? search = null,
            [FromQuery] string? status = null,
            [FromQuery] int page = 1,
            [FromQuery] int pageSize = 10,
            [FromQuery] bool includeContact = false)
        {
            var result = await _userRepository.GetUsersAsync(search, status, page, pageSize);

            var userDtos = result.Data.Select(u => new UserDto
            {
                Id = u.Id,
                FirstName = u.FirstName ?? "",
                LastName = u.LastName ?? "",
                Email = includeContact ? (u.Email ?? "") : "",
                Status = GetStatusFromApprovalStatus(u.ApprovalStatus)
            }).ToList();

            return Ok(new PagedResultDto<UserDto>
            {
                Data = userDtos,
                TotalCount = result.TotalCount,
                Page = result.Page,
                PageSize = result.PageSize,
                TotalPages = result.TotalPages
            });
        }

        [HttpGet("{id}")]
        public async Task<ActionResult<UserDto>> GetUser(int id, [FromQuery] bool includeContact = false)
        {
            var user = await _userRepository.GetByIdAsync(id);

            if (user == null)
            {
                return NotFound();
            }

            return Ok(new UserDto
            {
                Id = user.Id,
                FirstName = user.FirstName ?? "",
                LastName = user.LastName ?? "",
                Email = includeContact ? (user.Email ?? "") : "",
                Status = GetStatusFromApprovalStatus(user.ApprovalStatus)
            });
        }

        [HttpPost]
        public async Task<ActionResult<UserDto>> CreateUser([FromBody] CreateUserDto dto)
        {
            var user = new User
            {
                FirstName = dto.FirstName,
                LastName = dto.LastName,
                Email = dto.Email,
                Phone = dto.Phone,
                Role = dto.Role,
                ApprovalStatus = dto.ApprovalStatus ?? "Pending"
            };

            var createdUser = await _userRepository.CreateAsync(user);

            return CreatedAtAction(nameof(GetUser), new { id = createdUser.Id }, new UserDto
            {
                Id = createdUser.Id,
                FirstName = createdUser.FirstName ?? "",
                LastName = createdUser.LastName ?? "",
                Email = createdUser.Email ?? "",
                Status = GetStatusFromApprovalStatus(createdUser.ApprovalStatus)
            });
        }

        [HttpPut("{id}")]
        public async Task<IActionResult> UpdateUser(int id, [FromBody] UpdateUserDto dto)
        {
            var user = await _userRepository.GetByIdAsync(id);

            if (user == null)
            {
                return NotFound();
            }

            if (!string.IsNullOrEmpty(dto.FirstName))
                user.FirstName = dto.FirstName;
            if (!string.IsNullOrEmpty(dto.LastName))
                user.LastName = dto.LastName;
            if (!string.IsNullOrEmpty(dto.Email) && dto.Email != user.Email)
                return BadRequest();
            if (!string.IsNullOrEmpty(dto.Phone))
                user.Phone = dto.Phone;
            if (!string.IsNullOrEmpty(dto.ApprovalStatus))
                user.ApprovalStatus = dto.ApprovalStatus;

            await _userRepository.UpdateAsync(user);

            return NoContent();
        }

        [HttpDelete("{id}")]
        public async Task<IActionResult> DeleteUser(int id)
        {
            var user = await _userRepository.GetByIdAsync(id);
            if (user == null)
            {
                return NotFound();
            }

            await _userRepository.DeleteAsync(user);

            return NoContent();
        }

        [HttpPatch("{id}/status")]
        public async Task<IActionResult> UpdateUserStatus(int id, [FromBody] UpdateStatusDto dto)
        {
            var user = await _userRepository.GetByIdAsync(id);
            if (user == null)
            {
                return NotFound();
            }

            user.ApprovalStatus = GetApprovalStatusFromStatus(dto.Status);
            await _userRepository.UpdateAsync(user);

            return Ok(new UserDto
            {
                Id = user.Id,
                FirstName = user.FirstName ?? "",
                LastName = user.LastName ?? "",
                Email = user.Email ?? "",
                Status = GetStatusFromApprovalStatus(user.ApprovalStatus)
            });
        }

        [HttpGet("activation-requests")]
        public async Task<ActionResult<PagedResultDto<UserDto>>> GetActivationRequests(
            [FromQuery] int page = 1,
            [FromQuery] int pageSize = 10)
        {
            var result = await _userRepository.GetActivationRequestsAsync(page, pageSize);

            var userDtos = result.Data.Select(u => new UserDto
            {
                Id = u.Id,
                FirstName = u.FirstName ?? "",
                LastName = u.LastName ?? "",
                Email = u.Email ?? "",
                Status = GetStatusFromApprovalStatus(u.ApprovalStatus)
            }).ToList();

            return Ok(new PagedResultDto<UserDto>
            {
                Data = userDtos,
                TotalCount = result.TotalCount,
                Page = result.Page,
                PageSize = result.PageSize,
                TotalPages = result.TotalPages
            });
        }

        private string GetStatusFromApprovalStatus(string? approvalStatus)
        {
            return approvalStatus switch
            {
                "Approved" => "Active",
                "Rejected" => "Blocked",
                "Pending" => "Non-Active",
                _ => "Non-Active"
            };
        }

        private string GetApprovalStatusFromStatus(string status)
        {
            return status switch
            {
                "Active" => "Approved",
                "Blocked" => "Rejected",
                "Non-Active" => "Pending",
                _ => "Pending"
            };
        }
    }
}
