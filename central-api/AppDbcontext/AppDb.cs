using Microsoft.EntityFrameworkCore;

namespace BirdLab;



public class AppDb(DbContextOptions<AppDb> options) : DbContext(options)
{
    public DbSet<BirdRecord> History => Set<BirdRecord>();
}