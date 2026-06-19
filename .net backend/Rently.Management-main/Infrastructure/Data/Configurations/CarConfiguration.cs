using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using Rently.Management.Domain.Entities;

namespace Rently.Management.Infrastructure.Data.Configurations
{
    public class CarConfiguration : IEntityTypeConfiguration<Car>
    {
        public void Configure(EntityTypeBuilder<Car> builder)
        {
            builder.ToTable("Cars");

            builder.HasKey(c => c.Id);
            builder.Property(c => c.Id).ValueGeneratedOnAdd();

            builder.Property(c => c.Brand).HasMaxLength(100).IsRequired();
            builder.Property(c => c.Model).HasMaxLength(100).IsRequired();
            builder.Property(c => c.Transmission).HasMaxLength(50);
            builder.Property(c => c.Color).HasMaxLength(50);
            builder.Property(c => c.LocationCity).HasMaxLength(100);
            builder.Property(c => c.Features).HasMaxLength(1000);
            builder.Property(c => c.Description).HasMaxLength(2000);
            builder.Property(c => c.LicensePlate).HasMaxLength(20).IsRequired();
            builder.Property(c => c.CarLicenseImage).HasMaxLength(500);

            // PricePerDay - key decimal field
            builder.Property(c => c.PricePerDay)
                   .HasPrecision(18, 2)
                   .IsRequired();

            builder.Property(c => c.AverageRating)
                   .HasPrecision(3, 2); // e.g., 4.75

            // Indexes
            builder.HasIndex(c => c.LicensePlate).IsUnique();
            builder.HasIndex(c => c.OwnerId);

            // Relationships
            builder.HasOne(c => c.Owner)
                   .WithMany(u => u.OwnedCars)
                   .HasForeignKey(c => c.OwnerId)
                   .OnDelete(DeleteBehavior.Restrict);

            builder.HasMany(c => c.Bookings)
                   .WithOne(b => b.Car)
                   .HasForeignKey(b => b.CarId)
                   .OnDelete(DeleteBehavior.Restrict);

            builder.HasMany(c => c.Reviews)
                   .WithOne(r => r.Car)
                   .HasForeignKey(r => r.CarId)
                   .OnDelete(DeleteBehavior.Restrict);

            builder.HasMany(c => c.Images)
                   .WithOne(i => i.Car)
                   .HasForeignKey(i => i.CarId)
                   .OnDelete(DeleteBehavior.Cascade);

            builder.HasMany(c => c.UnavailableDates)
                   .WithOne(d => d.Car)
                   .HasForeignKey(d => d.CarId)
                   .OnDelete(DeleteBehavior.Cascade);

            builder.HasMany(c => c.Favorites)
                   .WithOne(f => f.Car)
                   .HasForeignKey(f => f.CarId)
                   .OnDelete(DeleteBehavior.Cascade);
        }
    }
}
