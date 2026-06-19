using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using Rently.Management.Domain.Entities;

namespace Rently.Management.Infrastructure.Data.Configurations
{
    public class ReviewConfiguration : IEntityTypeConfiguration<Review>
    {
        public void Configure(EntityTypeBuilder<Review> builder)
        {
            builder.ToTable("Reviews");

            builder.HasKey(r => r.Id);
            builder.Property(r => r.Id).ValueGeneratedOnAdd();

            builder.Property(r => r.Comment).HasMaxLength(2000);

            builder.HasOne(r => r.Renter)
                   .WithMany(u => u.Reviews)
                   .HasForeignKey(r => r.RenterId)
                   .OnDelete(DeleteBehavior.Restrict);

            builder.HasOne(r => r.Car)
                   .WithMany(c => c.Reviews)
                   .HasForeignKey(r => r.CarId)
                   .OnDelete(DeleteBehavior.Restrict);
        }
    }
}