using System.Security.Cryptography;
using System.Text;

namespace Rently.Management.WebApi.Services
{
    public class PasswordService
    {
        public (string hash, string salt) HashPassword(string password)
        {
            var saltBytes = RandomNumberGenerator.GetBytes(16);
            var salt = Convert.ToBase64String(saltBytes);
            var hash = HashWithSalt(password, salt);
            return (hash, salt);
        }

        public bool Verify(string password, string hash, string salt)
        {
            var computed = HashWithSalt(password, salt);
            return CryptographicOperations.FixedTimeEquals(Encoding.UTF8.GetBytes(computed), Encoding.UTF8.GetBytes(hash));
        }

        private string HashWithSalt(string password, string salt)
        {
            using var derive = new Rfc2898DeriveBytes(password, Convert.FromBase64String(salt), 100_000, HashAlgorithmName.SHA256);
            var key = derive.GetBytes(32);
            return Convert.ToBase64String(key);
        }
    }
}
