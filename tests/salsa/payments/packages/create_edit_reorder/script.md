# Create, edit and reorder packages with products — Detailed Script

Core BO package-management flow. UI locator decisions live in packages_helpers.py.

## Actions
1. Create a product `payable_item1` ($10) via API (`create_product_via_api`).
2. Create a fresh client via API (`make_client`) — legacy Background; not asserted here.
3. Create `package_1` via UI (`create_package`): service `service`, 2cr, $150, product
   `payable_item1` x2, add-ons enabled (`#myonoffswitch_NaN`, product autocomplete,
   `name='dummyProductQuantity'`).
4. Create `package_2` via UI: any-service `r2p_event`, 3cr, $250, product x3, add-ons enabled.
   (`r2p_event` is an event service; legacy puts it in a package via the "any service" picker,
   so `package_type="any"`, `service_list=["r2p_event"]`.)
5. Assert list order `[package_1, package_2]` (`assert_packages_list_order`; list rows read from
   `div.title.ng-binding`).
6. Edit `package_1` via UI (`edit_package`): rename `package_3`, disable add-ons.
7. Assert list order `[package_3, package_2]`.
8. Reorder via API (`reorder_packages_api`; legacy "reorder packages by API").
9. Assert list order `[package_2, package_3]`.

## Success Verification
- List reflects create, rename, and reorder in order.
