odoo.define("website_sale_livam.checkout", function (require) {
    "use strict";

    const publicWidget = require("web.public.widget");
    const ajax = require("web.ajax");

    publicWidget.registry.LivamCheckout = publicWidget.Widget.extend({
        selector: "#livam_tenant_form",

        events: {
            "change input[name='livam_tenant_slug']": "_onChange",
            "change input[name='livam_domain']": "_onChange",
        },

        _onChange: function () {
            const slug = this.$("input[name='livam_tenant_slug']").val().trim();
            const domain = this.$("input[name='livam_domain']").val().trim();
            const status = this.$("#livam_availability");
            if (!slug && !domain) {
                status.text("").removeClass("text-success text-danger");
                return;
            }
            ajax.jsonRpc("/shop/livam/check_availability", "call", {
                tenant_slug: slug,
                domain: domain,
            })
                .then((result) => {
                    if (result.available === true) {
                        status.text("Verfügbar")
                            .removeClass("text-danger")
                            .addClass("text-success");
                    } else if (result.available === false) {
                        status.text("Bereits vergeben")
                            .removeClass("text-success")
                            .addClass("text-danger");
                    } else {
                        status.text("");
                    }
                })
                .guardedCatch(function () {
                    status.text("");
                });
        },
    });
});
