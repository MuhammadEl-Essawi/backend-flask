using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using Rently.Management.Domain.Entities;

namespace Rently.Management.Infrastructure.Data.Configurations
{
    public class BookingConfiguration : IEntityTypeConfiguration<Booking>
    {
        public void Configure(EntityTypeBuilder<Booking> builder)
        {
            builder.ToTable("Bookings");

            builder.HasKey(b => b.Id);
            builder.Property(b => b.Id).ValueGeneratedOnAdd();

            builder.Property(b => b.Status).HasMaxLength(50).IsRequired();
            builder.Property(b => b.TransactionId).HasMaxLength(100);

            // Indexes
            builder.HasIndex(b => b.TransactionId).IsUnique();

            // Relationships
            builder.HasOne(b => b.Car)
                   .WithMany(c => c.Bookings)
                   .HasForeignKey(b => b.CarId)
                   .OnDelete(DeleteBehavior.Restrict);

            builder.HasOne(b => b.Renter)
                   .WithMany(u => u.BookingsAsRenter)
                   .HasForeignKey(b => b.RenterId)
                   .OnDelete(DeleteBehavior.Restrict);
        }
    }
}
