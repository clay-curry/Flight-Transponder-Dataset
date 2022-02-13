function fetchData(options) {
    options = options || {};
    if (heatmap || replay || showTrace || pTracks || !loadFinished)
        return;
    let currentTime = new Date().getTime();

    if (!options.force && (currentTime - lastFetch < refreshInt() || pendingFetches > 0)) {
        return;
    }
    if (debugFetch)
        console.log((currentTime - lastFetch) / 1000);
    lastFetch = currentTime;

    FetchPending = [];
    if (FetchPendingUAT != null) {
        // don't double up on fetches, let the last one resolve
        return;
    }

    //console.timeEnd("Starting Fetch");
    //console.time("Starting Fetch");

    if (enable_uat) {
        FetchPendingUAT = jQuery.ajax({
            url: 'chunks/978.json',
            dataType: 'json'
        });

        FetchPendingUAT.done(function (data) {
            uat_data = data;
            FetchPendingUAT = null;
        });
        FetchPendingUAT.fail(function (jqxhr, status, error) {
            FetchPendingUAT = null;
        });
    }

    let ac_url = [];
    if (uuid != null) {
        for (let i in uuid) {
            ac_url.push('uuid/?feed=' + uuid[i]);
        }
    } else if (globeIndex) {
        let indexes = globeIndexes();
        const ancient = (currentTime - 2 * refreshInt() / globeSimLoad * globeTilesViewCount) / 1000;
        for (let i in indexes) {
            const k = indexes[i];
            if (globeIndexNow[k] < ancient) {
                globeIndexNow[k] = null;
            }
        }
        indexes.sort(function (x, y) {
            if (!globeIndexNow[x] && !globeIndexNow[y]) {
                return globeIndexDist[x] - globeIndexDist[y];
            }
            if (globeIndexNow[x] == null)
                return -1;
            if (globeIndexNow[y] == null)
                return 1;
            return (globeIndexNow[x] - globeIndexNow[y]);
        });

        if (binCraft && onlyMilitary && ZoomLvl < 5.5) {
            ac_url.push('data/globeMil_42777.binCraft');
        } else {

            indexes = indexes.slice(0, globeSimLoad);

            let suffix = binCraft ? '.binCraft' : '.json'
            let mid = (binCraft && onlyMilitary) ? 'Mil_' : '_';
            for (let i in indexes) {
                ac_url.push('data/globe' + mid + indexes[i].toString().padStart(4, '0') + suffix);
            }
        }
    } else if (binCraft) {
        ac_url.push('data/aircraft.binCraft');
    } else {
        ac_url.push('data/aircraft.json');
    }

    pendingFetches += ac_url.length;
    fetchCounter += ac_url.length;

    for (let i in ac_url) {
        //console.log(ac_url[i]);
        let req;
        if (binCraft) {
            req = jQuery.ajax({
                url: `${ac_url[i]}`, method: 'GET',
                xhr: arraybufferRequest,
                timeout: 15000,
                urlIndex: i
            });
        } else {
            req = jQuery.ajax({ url: `${ac_url[i]}`, dataType: 'json', urlIndex: i });
        }
        FetchPending.push(req);

        req
            .done(function (data) {
                pendingFetches--;
                if (data == null) {
                    return;
                }
                if (binCraft) {
                    data = { buffer: data, };
                    wqi(data);
                }
                data.urlIndex = this.urlIndex;

                if (!data.aircraft || !data.now) {
                    let error = data.error;
                    if (error) {
                        jQuery("#update_error_detail").text(error);
                        jQuery("#update_error").css('display', 'block');
                        StaleReceiverCount++;
                    }
                    return;
                }

                //console.time("Process " + data.globeIndex);
                processReceiverUpdate(data);
                //console.timeEnd("Process " + data.globeIndex);
                data = null;

                if (uat_data) {
                    processReceiverUpdate(uat_data);
                    uat_data = null;
                }

                if (pendingFetches <= 0 && !tabHidden) {
                    triggerRefresh++;
                    checkMovement();
                    if (firstFetch) {
                        firstFetch = false;
                        if (uuid) {
                            const ext = myExtent(OLMap.getView().calculateExtent(OLMap.getSize()));
                            let jump = true;
                            for (let i = 0; i < PlanesOrdered.length; ++i) {
                                const plane = PlanesOrdered[i];
                                if (plane.visible && inView(plane.position, ext)) {
                                    jump = false;
                                    break;
                                }
                            }
                            if (jump) {
                                followRandomPlane();
                                deselectAllPlanes();
                                OLMap.getView().setZoom(6);
                            }
                        }
                        checkRefresh();
                    }
                }


                // Check for stale receiver data
                if (last == now && !globeIndex) {
                    StaleReceiverCount++;
                    if (StaleReceiverCount > 5) {
                        jQuery("#update_error_detail").text("The data from the server hasn't been updated in a while.");
                        jQuery("#update_error").css('display', 'block');
                    }
                } else if (StaleReceiverCount > 0) {
                    StaleReceiverCount = 0;
                    jQuery("#update_error").css('display', 'none');
                }
            })
            .fail(function (jqxhr, status, error) {
                pendingFetches--;
                if (pendingFetches <= 0 && !tabHidden) {
                    triggerRefresh++;
                    checkMovement();
                }
                status = jqxhr.status;
                if (jqxhr.readyState == 0) error = "Can't connect to server, check your network!";
                let errText = status + (error ? (": " + error) : "");
                console.log(jqxhr);
                console.log(error);
                if (status != 429 && status != '429') {
                    jQuery("#update_error_detail").text(errText);
                    jQuery("#update_error").css('display', 'block');
                    StaleReceiverCount++;
                } else {
                    if (C429++ > 16) {
                        globeRateUpdate();
                        C429 = 0;
                    }
                }
            });
    }
}