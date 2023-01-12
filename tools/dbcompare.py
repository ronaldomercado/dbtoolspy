#!/usr/bin/env python
"""
This script loads two sets of records from substitution files
and compares them

"""
import argparse
import os
import dbtoolspy

def dbsort(path):
    """
    returns a database with the records ordered
    """
    db = dbtoolspy.load_database_file(path)
    database = dbtoolspy.Database()
    for rec in sorted(db.items(), key = lambda x: x[0]):
        database.add_record(rec[1])
    return database

def getElem(db):
    """
    Remove and return element from the end of the 'db'
    OrderedDictionary (destructive change of 'db').
    returns None when db is empty
    """
    if len(db) > 0:
        item = db.popitem(last=False)
        return item
    else:
        return None

def reportRemaining(r, db,  dbname='first'):
    """
    Report the record 'r' and the remaining entries from Database 'db'.
    dbname - use 'first' or 'second' for the output message.
    """
    if r is not None:
        print("Record %s missing in %s (%s)" % (dbname,r[0]))
    elem = getElem(db)
    while elem:
        print("Record %s missing in %s (%s)" % (dbname,elem[0]))
        elem = getElem(db)

def reportMissingFields(f, rec,recname="first"):
    """
    Report the field 'f' and the remaining entries from Record 'rec'
    recname - use 'first' or 'second' for the output message
    """
    if f is not None:
        print("  Field %s missing in %s record" % (f[0], recname))
    elem = getElem(rec.fields)
    while elem:
        print("  Field %s missing in %s Record" % (elem[0], recname))
        elem = getElem(rec.fields)

def fieldsort(rec):
    """
    returns a field-sorted copy of the record
    """
    record = dbtoolspy.Record()
    record.name = rec.name
    record.rtyp= rec.rtyp
    for f in sorted(rec.fields.keys()):
        record.fields[f] = rec.fields[f]
    return record

def recCompare(rec1,rec2):
    """
    generate a field comparison report for Records rec1 and rec2
    """
    assert rec1.name == rec2.name, "Record names don't match!"
    r1 = fieldsort(rec1)
    r2 = fieldsort(rec2)
    f1 = getElem(r1.fields)
    f2 = getElem(r2.fields)
    announce = False
    while True:
        both_exist = f1 is not None and f2 is not None
        if both_exist:
            if f1[0] == f2[0]:
                if f1[1] != f2[1]:
                    print("Mismatch in Record %s" % r1.name )
                    announce = True
                    print("  Field values mismatch %s" % f1[0])
                    print("    val1 %s" % f1[1])
                    print("    val2 %s" % f2[1])
                f1 = getElem(r1.fields)
                f2 = getElem(r2.fields)
            elif f1[0] < f2[0]:
                if not announce:
                    print("Mismatch in Record %s" % r1.name )
                    announce = True
                print("  Field %s missing in second record" % f1[0])
                f1 = getElem(r1.fields)
            else:
                if not announce:
                    print("Mismatch in Record %s" % r1.name )
                    announce = True
                print("  Field %s missing in first record" % f2[0])
                f2 = getElem(r2.fields)
        elif f1 is None:
            reportMissingFields(f2, r2, "first")
            break
        else:
            reportMissingFields(f1, r1, "second")
            break

def dbcompare(path1, path2, nofields=False):
    """
    Compare databases from two paths.
    The comparison depends on ordered entries
    """
    db1 = dbsort(path1)
    db2 = dbsort(path2)
    if nofields:
        print("Comparing dbs (w/o fields)")
    else:
        print("Comparing dbs")
    print("  First db: %s" % path1)
    print("  No records = %d\n" % len(db1))
    print("  Second db: %s " % path2)
    print("  No records = %d\n" % len(db2))

    elem1 = getElem(db1)
    elem2 = getElem(db2)
    while True:
        both_exist = elem1 is not None and elem2 is not None
        if both_exist:
            if elem1[0] == elem2[0]:
                if not nofields:
                    # fields comparison
                    recCompare(elem1[1],elem2[1])
                elem1 = getElem(db1)
                elem2 = getElem(db2)
            elif elem1[0] < elem2[0]:
                print("Record %s missing in second db" % elem1[0])
                elem1 = getElem(db1)
            else:
                # B2
                print("Record %s missing in first db" % elem2[0])
                elem2 = getElem(db2)
        elif elem1 is None:
            reportRemaining(elem2,db2, dbname='second')
            break
        else:
            assert elem2 is None, "elem2 should be at its end...."
            reportRemaining(elem1,db1, dbname='first')
            break


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-n','--nofields', action='store_true',
            help = 'no field mismatches reporting')
    parser.add_argument('db1',
            help='First db file')
    parser.add_argument('db2',
            help='Second db file')
    args = parser.parse_args()

    db1path = os.path.expanduser(args.db1)
    db2path = os.path.expanduser(args.db2)

    dbcompare(db1path, db2path, args.nofields)
