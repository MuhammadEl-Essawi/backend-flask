using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using Rently.Management.Domain.Entities;

namespace Rently.Management.Infrastructure.Data.Configurations
{
    public class UserConfiguration : IEntityTypeConfiguration<User>
    {
        public void Configure(EntityTypeBuilder<User> builder)
        {
            builder.ToTable("Users");

            builder.HasKey(u => u.Id);
            builder.Property(u => u.Id).ValueGeneratedOnAdd();

            builder.Property(u => u.FirstName).HasMaxLength(150);
            builder.Property(u => u.LastName).HasMaxLength(150);
            builder.Property(u => u.Email).HasMaxLength(255);
            builder.Property(u => u.IsSuperAdmin).HasDefaultValue(false);
            builder.Property(u => u.Phone).HasMaxLength(30);
            builder.Property(u => u.Role).HasMaxLength(50);
            builder.Property(u => u.Nationality).HasMaxLength(100);
            builder.Property(u => u.PreferredLanguage).HasMaxLength(50);
            builder.Property(u => u.LicenseNumber).HasMaxLength(50);
            builder.Property(u => u.ApprovalStatus).HasMaxLength(50);
            builder.Property(u => u.PayoutMethod).HasMaxLength(50);
            builder.Property(u => u.PayoutDetails).HasMaxLength(500);
            builder.Property(u => u.BillingCountry).HasMaxLength(100);
            builder.Property(u => u.ZipCode).HasMaxLength(20);

            builder.Property(u => u.PasswordHash).HasMaxLength(256);
            builder.Property(u => u.PasswordSalt).HasMaxLength(128);
            builder.Property(u => u.PasswordResetToken).HasMaxLength(128);

            // Images (paths or URLs)
            builder.Property(u => u.IdImage).HasMaxLength(500);
            builder.Property(u => u.LicenseImage).HasMaxLength(500);
            builder.Property(u => u.PassportImage).HasMaxLength(500);
            builder.Property(u => u.SelfieImage).HasMaxLength(500);
            builder.Property(u => u.ResidenceProofImage).HasMaxLength(500);
            builder.Property(u => u.JobProofImage).HasMaxLength(500);

            // Useful indexes
            builder.HasIndex(u => u.Email).IsUnique();
            builder.HasIndex(u => u.Phone).IsUnique();
            builder.HasIndex(u => u.LicenseNumber).IsUnique();

            // Relationships
            builder.HasMany(u => u.OwnedCars)
                   .WithOne(c => c.Owner)
                   .HasForeignKey(c => c.OwnerId)
                   .OnDelete(DeleteBehavior.Restrict); // Do not delete cars when a user is deleted

            builder.HasMany(u => u.BookingsAsRenter)
                   .WithOne(b => b.Renter)
                   .HasForeignKey(b => b.RenterId)
                   .OnDelete(DeleteBehavior.Restrict);

            builder.HasMany(u => u.Reviews)
                   .WithOne(r => r.Renter)
                   .HasForeignKey(r => r.RenterId)
                   .OnDelete(DeleteBehavior.Restrict);

            builder.HasMany(u => u.Notifications)
                   .WithOne(n => n.User)
                   .HasForeignKey(n => n.UserId)
                   .OnDelete(DeleteBehavior.Cascade);

            builder.HasMany(u => u.Favorites)
                   .WithOne(f => f.User)
                   .HasForeignKey(f => f.UserId)
                   .OnDelete(DeleteBehavior.Cascade);

            builder.HasMany(u => u.SentMessages)
                   .WithOne(m => m.Sender)
                   .HasForeignKey(m => m.SenderId)
                   .OnDelete(DeleteBehavior.Restrict);

            builder.HasMany(u => u.ReceivedMessages)
                   .WithOne(m => m.Receiver)
                   .HasForeignKey(m => m.ReceiverId)
                   .OnDelete(DeleteBehavior.Restrict);

            builder.HasMany(u => u.Otps)
                   .WithOne(o => o.User)
                   .HasForeignKey(o => o.UserId)
                   .OnDelete(DeleteBehavior.Cascade);
        }
    }
}
