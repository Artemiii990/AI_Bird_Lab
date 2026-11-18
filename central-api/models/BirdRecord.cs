namespace BirdLab;

public class BirdRecord
{
    public int Id { get; set; }
    public string FileName { get; set; } = "";
    public string Species { get; set; } = "";
    public double Confidence { get; set; }
    public string Description { get; set; } = "";
    public DateTime Date { get; set; } = DateTime.UtcNow;
}