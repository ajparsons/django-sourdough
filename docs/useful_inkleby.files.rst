
.. _useful_inkleby.files:

useful_inkleby.files package
============================
        
QuickGrid Usage
-------------------------------------
        
.. code-block:: python
        
    grid = QuickGrid().open(FILEPATH)
    
    for r in grid:
        #for each row
        print r["foo"] #print the value for the column called "foo"
    
    for r in grid.only("city","london"):
        #for each row
        print r["foo"]

    for r in grid.exclude("fruit","banana"):
        #for each row
        print r["foo"]
        
    
useful_inkleby.files.quickgrid module
-------------------------------------

.. automodule:: useful_inkleby.files.quickgrid
    :members:
    :undoc-members:
    :show-inheritance:
    
