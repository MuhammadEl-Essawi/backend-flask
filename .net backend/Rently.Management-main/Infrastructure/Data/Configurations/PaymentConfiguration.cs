using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using Rently.Management.Domain.Entities;

namespace Rently.Management.Infrastructure.Data.Configurations
{
    public class PaymentConfiguration : IEntityTypeConfiguration<Payment>
    {
        public void Configure(EntityTypeBuilder<Payment> builder)
        {
            builder.ToTable("Payments");

            builder.HasKey(p => p.Id);
            builder.Property(p => p.Id).ValueGeneratedOnAdd();

            builder.Property(p => p.Amount)
                   .IsRequired();

            builder.Property(p => p.Currency)
                   .HasMaxLength(10)
                   .IsRequired();

            builder.Property(p => p.Status)
                   .HasMaxLength(50)
                   .IsRequired();

            builder.Property(p => p.Provider)
                   .HasMaxLength(100);

            builder.Property(p => p.ProviderPaymentId)
                   .HasMaxLength(150);

            builder.Property(p => p.ProviderReceiptUrl)
                   .HasMaxLength(500);

            builder.Property(p => p.FailureCode)
                   .HasMaxLength(100);

            builder.Property(p => p.FailureMessage)
                   .HasMaxLength(1000);

            // Indexes useful for search and tracking operations
            builder.HasIndex(p => p.BookingId);
            builder.HasIndex(p => p.UserId);
            builder.HasIndex(p => p.ProviderPaymentId).IsUnique(false);

            // Relationships
            builder.HasOne(p => p.Booking)
                   .WithMany(b => b.Payments)
                   .HasForeignKey(p => p.BookingId)
                   .OnDelete(DeleteBehavior.Cascade);

            builder.HasOne(p => p.User)
                   .WithMany(u => u.Payments)
                   .HasForeignKey(p => p.UserId)
                   .OnDelete(DeleteBehavior.SetNull);
        }
    }
}

