import csv
import os
import textwrap
from collections import Counter
import platform

def clear_screen():
    """Clear terminal screen based on OS"""
    if platform.system() == "Windows":
        os.system('cls')
    else:
        os.system('clear')

def analyze_csv(file_path):
    """
    Efficient CSV analysis with essential metrics
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        # Read sample lines for dialect detection
        sample = f.read(10240)
        f.seek(0)
        
        # Detect CSV format
        dialect = csv.Sniffer().sniff(sample)
        has_header = csv.Sniffer().has_header(sample)
        reader = csv.reader(f, dialect)
        
        # Process headers
        headers = next(reader) if has_header else [f"Column {i+1}" for i in range(len(next(reader)))]
        f.seek(0)
        if has_header: next(reader)  # Skip header row
        
        # Collect essential statistics
        column_stats = [{
            'name': header,
            'type': 'unknown',
            'empty': 0,
            'unique': set(),
            'sample': []
        } for header in headers]
        
        row_count = 0
        for row in reader:
            row_count += 1
            for i, value in enumerate(row):
                if i >= len(headers):  # Handle columns with missing headers
                    continue
                    
                # Update statistics
                col = column_stats[i]
                col['unique'].add(value)
                
                if not value.strip():
                    col['empty'] += 1
                
                # Capture sample values
                if len(col['sample']) < 5 and value.strip():
                    col['sample'].append(value)
                
                # Detect data type
                if value.strip():
                    if col['type'] == 'unknown':
                        if value.replace('.', '', 1).isdigit():
                            col['type'] = 'number'
                        else:
                            col['type'] = 'text'
                    elif col['type'] == 'number' and not value.replace('.', '', 1).isdigit():
                        col['type'] = 'mixed'
        
        # Finalize stats
        for col in column_stats:
            col['unique_count'] = len(col['unique'])
            col['empty_pct'] = col['empty'] / row_count * 100 if row_count else 0
            del col['unique']  # No longer needed
    
    return {
        'file_name': os.path.basename(file_path),
        'headers': headers,
        'row_count': row_count,
        'column_stats': column_stats
    }

def display_summary(report):
    """Display clean summary report"""
    clear_screen()
    print(f"\n📊 CSV ANALYSIS REPORT: {report['file_name']}")
    print("=" * 60)
    print(f"• Total Rows: {report['row_count']:,}")
    print(f"• Total Columns: {len(report['headers'])}")
    print("\n🔍 COLUMN SUMMARY")
    print("=" * 60)
    
    # Column headers
    print(f"{'Column':<20} {'Type':<10} {'Unique':<10} {'Empty':<10} Sample Values")
    print("-" * 60)
    
    # Column details
    for col in report['column_stats']:
        sample = ', '.join([v[:20] + '...' if len(v) > 20 else v for v in col['sample']])
        print(f"{col['name'][:18]:<20} {col['type']:<10} {col['unique_count']:<10,} {col['empty_pct']:>5.1f}%    {sample}")

def display_column_details(report, col_index):
    """Show detailed column analysis"""
    col = report['column_stats'][col_index]
    
    clear_screen()
    print(f"\n🔎 DETAILED ANALYSIS: {col['name']}")
    print("=" * 60)
    print(f"• Column Type: {col['type'].upper()}")
    print(f"• Unique Values: {col['unique_count']:,}")
    print(f"• Empty Values: {col['empty']:,} ({col['empty_pct']:.1f}%)")
    
    if col['type'] in ('number', 'mixed'):
        try:
            # Convert to numbers if possible
            numbers = [float(v) for v in col['sample'] if v.replace('.', '', 1).isdigit()]
            if numbers:
                print(f"\n📈 Number Analysis:")
                print(f"  • Min: {min(numbers):,.2f}")
                print(f"  • Max: {max(numbers):,.2f}")
                print(f"  • Avg: {sum(numbers)/len(numbers):,.2f}")
        except:
            pass
    
    if col['unique_count'] <= 20:
        print("\n🌟 All Unique Values:")
        for value in sorted(col['sample']):
            print(f"  • {value}")
    elif col['unique_count'] > 20:
        print("\n🌟 Common Values:")
        for value in col['sample'][:5]:
            print(f"  • {value}")

def main():
    """Main application function"""
    clear_screen()
    print("\n" + "=" * 50)
    print("📂 CSV INSIGHT ANALYZER")
    print("=" * 50)
    
    while True:
        file_path = input("\nEnter CSV file path (or 'exit'): ").strip()
        if file_path.lower() in ['exit', 'quit']:
            break
            
        if not os.path.exists(file_path):
            print(f"🚨 File not found: {file_path}")
            continue
            
        try:
            report = analyze_csv(file_path)
            display_summary(report)
            
            while True:
                print("\n" + "=" * 60)
                print("OPTIONS: [1-9] Column Details | [R]efresh | [N]ew File | [Q]uit")
                choice = input("Select: ").strip().lower()
                
                if choice == 'q':
                    return
                elif choice == 'n':
                    break
                elif choice == 'r':
                    display_summary(report)
                elif choice.isdigit():
                    col_index = int(choice) - 1
                    if 0 <= col_index < len(report['headers']):
                        display_column_details(report, col_index)
                    else:
                        print("Invalid column number!")
                else:
                    print("Invalid option!")
                    
        except Exception as e:
            print(f"🚨 Error processing file: {str(e)}")

if __name__ == "__main__":
    main()
