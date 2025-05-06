# database_updater.py
import sqlite3
from fast_recommendations import FastRecommendationEngine
from tqdm import tqdm
import time
from datetime import timedelta

class DatabaseUpdater:
    def __init__(self, db_name='ecommerce.db'):
        self.engine = FastRecommendationEngine(db_name)
        self.stats = {
            'processed': 0,
            'skipped': 0,
            'start_time': time.time()
        }
    
    def _add_recommendation_columns(self):
        """Ensure recommendation columns exist"""
        with self.engine.conn as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(customers)")
            columns = [col[1] for col in cursor.fetchall()]
            
            for i in range(1, 6):
                col_name = f"recommendation{i}"
                if col_name not in columns:
                    cursor.execute(f"ALTER TABLE customers ADD COLUMN {col_name} TEXT")
                    print(f"Added column: {col_name}")
    
    def _update_customer_recommendations(self, customer_id):
        """Process recommendations for a single customer"""
        try:
            recs = self.engine.get_recommendations(customer_id)
            if not recs:
                self.stats['skipped'] += 1
                return None
            
            # Pad with None if less than 5 recommendations
            recs += [None] * (5 - len(recs))
            
            with self.engine.conn as conn:
                cursor = conn.cursor()
                cursor.execute("""
                UPDATE customers SET 
                    recommendation1 = ?,
                    recommendation2 = ?,
                    recommendation3 = ?,
                    recommendation4 = ?,
                    recommendation5 = ?
                WHERE Customer_ID = ?
                """, (*recs[:5], customer_id))
            
            self.stats['processed'] += 1
            return recs
        except Exception as e:
            self.stats['skipped'] += 1
            return None
    
    def _print_stats(self):
        """Display current statistics"""
        elapsed = time.time() - self.stats['start_time']
        rate = self.stats['processed'] / elapsed if elapsed > 0 else 0
        
        print(f"\n╔{'═'*50}╗")
        print(f"║ {'STATISTICS':^48} ║")
        print(f"╠{'═'*50}╣")
        print(f"║ {'Processed:':<30} {self.stats['processed']:>18} ║")
        print(f"║ {'Skipped:':<30} {self.stats['skipped']:>18} ║")
        print(f"║ {'Elapsed Time:':<30} {str(timedelta(seconds=int(elapsed))):>18} ║")
        print(f"║ {'Rate:':<30} {rate:>18.2f} cust/sec ║")
        print(f"╚{'═'*50}╝")
    
    def run(self):
        """Execute the full update process"""
        print("🚀 Starting recommendation database update...")
        self._add_recommendation_columns()
        
        total_customers = len(self.engine.customers)
        print(f"📊 Processing {total_customers} customers...\n")
        
        # Process with progress bar
        with tqdm(total=total_customers, unit='cust', 
                 bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]") as pbar:
            for _, row in self.engine.customers.iterrows():
                self._update_customer_recommendations(row['Customer_ID'])
                pbar.update(1)
                
                # Print stats every 100 customers
                if pbar.n % 100 == 0:
                    pbar.write("")  # New line
                    self._print_stats()
        
        # Final statistics
        self._print_stats()
        self.engine.close()
        print("\n✅ Database update completed successfully!")

if __name__ == "__main__":
    updater = DatabaseUpdater()
    updater.run()