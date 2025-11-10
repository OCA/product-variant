#  Copyright (c) 2025 Groupe Voltaire
#  @author Emilie SOUTIRAS  <emilie.soutiras@groupevoltaire.com>
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


def pre_init_hook(cr):
    # Preserve default_code already set on product
    cr.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = 'product_product'
                AND column_name = 'manual_code'
            ) THEN
                ALTER TABLE product_product ADD COLUMN manual_code BOOLEAN;
            END IF;
        END $$;
        """
    )
    cr.execute(
        """
        UPDATE product_product
        SET manual_code = true
        WHERE default_code is not NULL
    """
    )
