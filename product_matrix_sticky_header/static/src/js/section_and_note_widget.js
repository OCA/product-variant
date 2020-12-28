odoo.define("product_matrix_sticky_header.section_and_note_widget", function (require) {
    "use strict";
    var fieldRegistry = require("web.field_registry");
    require("product_matrix.section_and_note_widget");

    var SectionAndNoteFieldOne2Many = fieldRegistry.get("section_and_note_one2many");

    SectionAndNoteFieldOne2Many.include({
        /* eslint-disable no-unused-vars */
        _openMatrixConfigurator: function (
            jsonInfo,
            productTemplateId,
            editedCellAttributes
        ) {
            this._super.apply(this, arguments);
            this.fixOverflowTbodyStickyHeader();
        },
        /* eslint-enable no-unused-vars */
        fixOverflowTbodyStickyHeader: async function () {
            var found = false;
            var maxRetry = 5;
            while (!found && maxRetry > 0) {
                var table_matrix = $(".o_product_variant_matrix");
                found = table_matrix.length;
                await new Promise((resolve) => {
                    setTimeout(resolve, 100);
                });
                maxRetry--;
            }
            if (table_matrix) {
                table_matrix.parent().addClass("pt-0");
            }
        },
    });

    return SectionAndNoteFieldOne2Many;
});
